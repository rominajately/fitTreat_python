from flask import request
from flask.json import jsonify

from app.models.meal import Meal
from app.models.user import User
from attrdict import AttrDict
from mongoengine.errors import DoesNotExist
from mongoengine.queryset import QuerySet
from config import Config
from flask_api import status
from dateutil import tz, utils
from datetime import datetime, timedelta

from mongoengine import NotUniqueError

''' API to add new meal to the database'''
def addNewMeal():
    data = AttrDict(request.get_json())
    try:
        newMeal = Meal(
            name=data.name,
            foodPreference=data.foodPreference,
            cuisine=data.cuisine,
            dietType=[dt for dt in data.dietType],
            idealMedCond=[imc for imc in data.idealMedCond],
            avoidableMedCond=[amc for amc in data.avoidableMedCond],
            course=data.course,
            calories=data.calories,
            nutritionInfo=data.nutritionInfo,
            ingredients=data.ingredients,
            directions=data.directions,
            photoURL=Config.s3URL + data.photoURL
        ).save()
        return jsonify(newMeal), status.HTTP_200_OK
    except NotUniqueError:
        return jsonify({'stat:': 'Meal already exists.'}), status.HTTP_400_BAD_REQUEST
    except Exception as e:
        return jsonify({'Error': 'Error while saving meal - {}'.format(e)}), status.HTTP_500_INTERNAL_SERVER_ERROR


''' /* API to Add Meals in bulk to the database'''


def addMealData():
    meals_array = request.get_json()
    queryList = []
    for meal in meals_array:
        try:
            meal = Meal.objects.get(name=meal['name'])
        except DoesNotExist as dne:
            data = AttrDict(meal)
            newMeal = Meal(
                name=data.name,
                foodPreference=data.foodPreference,
                cuisine=data.cuisine,
                dietType=[dt for dt in data.dietType],
                idealMedCond=[imc for imc in data.idealMedCond],
                avoidableMedCond=[amc for amc in data.avoidableMedCond],
                course=data.course,
                calories=data.calories,
                nutritionInfo=data.nutritionInfo,
                ingredients=data.ingredients,
                directions=data.directions,
                photoURL=Config.s3URL + data.photoURL
            )
            queryList.append(newMeal)
    try:
        meals = Meal.objects.insert(queryList, load_bulk=True)
        return jsonify(meals), status.HTTP_200_OK
    except Exception as e:
        return jsonify({'Error': format(e)}), status.HTTP_400_BAD_REQUEST


'''

Meal Plan Generation Logic
/* Assign Meals to the user 
        - User's food preferences
        - User's Medical Condition
        - User's Timezone/Meal plan reset in 24H period

        - Meal Selection depending on the course - No Logic provided (Pending)
        - Meals limit - Total 15
            - Breakfast: 3
            - Lunch: 4
            - Dinner: 4
            - Snacks: 4
            * For Vegan
                - All 15 Vegan
            * For Vegetarian: Random Selection of Vegan + Vegetarian
                Vegan
                    Breakfast - 1
                    Lunch - 1
                    Dinner - 1
                    Snacks - 1
                Vegetarian
                    Breakfast - 2
                    Lunch - 3
                    Dinner - 3
                    Snacks - 3
            * For Non-Vegetarian - 5 Veg + Vegan (Random Selection) + 10 Non-Vegetarian
                Vegetarian
                    Breakfast - 1
                    Lunch - 1
                    Dinner - 1
                    Snacks - 1    
                Non-Vegetarian
                    Breakfast - 3
                    Lunch - 3
                    Dinner - 3
                    Snacks - 3
    
    */
'''


class meal_plan_count:
    vegan = {'Breakfast': 3, 'Lunch': 4, 'Dinner': 4, 'Snacks': 4}
    vegetarian = {'vegan': {'Breakfast': 1, 'Lunch': 1, 'Dinner': 1, 'Snacks': 1},
                  'vegetarian': {'Breakfast': 2, 'Lunch': 3, 'Dinner': 3, 'Snacks': 3}}
    non_veg = {'vegetarian': {'Breakfast': 1, 'Lunch': 1, 'Dinner': 1, 'Snacks': 1},
               'non_veg': {'Breakfast': 2, 'Lunch': 3, 'Dinner': 3, 'Snacks': 3}}


''' Method to fetch Vegan meals '''


def vegan_meals(assignedMealIds, usersMedicalCondition):
    vegan_plan_count = meal_plan_count.vegan
    breakfast = Meal.objects(id__nin=assignedMealIds, foodPreference__in=['Vegan'], course__in=['Breakfast'],
                             avoidableMedCond__nin=usersMedicalCondition)[:vegan_plan_count['Breakfast']]
    lunch = Meal.objects(id__nin=assignedMealIds, foodPreference__in=['Vegan'], course__in=['Lunch'],
                         avoidableMedCond__nin=usersMedicalCondition)[:vegan_plan_count['Lunch']]
    dinner = Meal.objects(id__nin=assignedMealIds, foodPreference__in=['Vegan'], course__in=['Dinner'],
                          avoidableMedCond__nin=usersMedicalCondition)[:vegan_plan_count['Dinner']]
    snacks = Meal.objects(id__nin=assignedMealIds, foodPreference__in=['Vegan'], course__in=['Snacks'],
                          avoidableMedCond__nin=usersMedicalCondition)[:vegan_plan_count['Snacks']]
    return list(breakfast) + list(lunch) + list(dinner) + list(snacks)


''' Method to fetch Vegetarian meals '''


def vegetarian_meals(assignedMealIds, usersMedicalCondition):
    # ****** Vegan Dishes ******
    vegan_plan_count = meal_plan_count.vegetarian['vegan']
    vega_breakfast = Meal.objects(id__nin=assignedMealIds, foodPreference__in=['Vegan'], course__in=['Breakfast'],
                                  avoidableMedCond__nin=usersMedicalCondition)[:vegan_plan_count['Breakfast']]
    vega_lunch = Meal.objects(id__nin=assignedMealIds, foodPreference__in=['Vegan'], course__in=['Lunch'],
                              avoidableMedCond__nin=usersMedicalCondition)[:vegan_plan_count['Lunch']]
    vega_dinner = Meal.objects(id__nin=assignedMealIds, foodPreference__in=['Vegan'], course__in=['Dinner'],
                               avoidableMedCond__nin=usersMedicalCondition)[:vegan_plan_count['Dinner']]
    vega_snacks = Meal.objects(id__nin=assignedMealIds, foodPreference__in=['Vegan'], course__in=['Snacks'],
                               avoidableMedCond__nin=usersMedicalCondition)[:vegan_plan_count['Snacks']]
    vega_meals = list(vega_breakfast) + list(vega_lunch) + list(vega_dinner) + list(vega_snacks)

    # ****** Vegetarian Dishes ******
    veget_plan_count = meal_plan_count.vegetarian['vegetarian']
    veg_breakfast = Meal.objects(id__nin=assignedMealIds, foodPreference__in=['Vegetarian'], course__in=['Breakfast'],
                                 avoidableMedCond__nin=usersMedicalCondition)[:veget_plan_count['Breakfast']]
    veg_lunch = Meal.objects(id__nin=assignedMealIds, foodPreference__in=['Vegetarian'], course__in=['Lunch'],
                             avoidableMedCond__nin=usersMedicalCondition)[:veget_plan_count['Lunch']]
    veg_dinner = Meal.objects(id__nin=assignedMealIds, foodPreference__in=['Vegetarian'], course__in=['Dinner'],
                              avoidableMedCond__nin=usersMedicalCondition)[:veget_plan_count['Dinner']]
    veg_snacks = Meal.objects(id__nin=assignedMealIds, foodPreference__in=['Vegetarian'], course__in=['Snacks'],
                              avoidableMedCond__nin=usersMedicalCondition)[:veget_plan_count['Snacks']]

    veg_meals = list(veg_breakfast) + list(veg_lunch) + list(veg_dinner) + list(veg_snacks)
    return vega_meals + veg_meals


''' Method to fetch Non-Vegetarian meals '''


def non_veg_meals(assignedMealIds, usersMedicalCondition):
    # ****** Vegetarian Dishes ******
    veg_plan_count = meal_plan_count.non_veg['vegetarian']
    veg_breakfast = Meal.objects(id__nin=assignedMealIds, foodPreference__in=['Vegetarian'], course__in=['Breakfast'],
                                 avoidableMedCond__ne=usersMedicalCondition)[:veg_plan_count['Breakfast']]
    veg_lunch = Meal.objects(id__nin=assignedMealIds, foodPreference__in=['Vegetarian'], course__in=['Lunch'],
                             avoidableMedCond__ne=usersMedicalCondition)[:veg_plan_count['Lunch']]
    veg_dinner = Meal.objects(id__nin=assignedMealIds, foodPreference__in=['Vegetarian'], course__in=['Dinner'],
                              avoidableMedCond__ne=usersMedicalCondition)[:veg_plan_count['Dinner']]
    veg_snacks = Meal.objects(id__nin=assignedMealIds, foodPreference__in=['Vegetarian'], course__in=['Snacks'],
                              avoidableMedCond__ne=usersMedicalCondition)[:veg_plan_count['Snacks']]
    veg_meals = list(veg_breakfast) + list(veg_lunch) + list(veg_dinner) + list(veg_snacks)
    print("Vege Meals : " + str(len(veg_meals)))

    # ****** Non-Vegetarian Dishes ******
    nonveg_plan_count = meal_plan_count.non_veg['non_veg']
    nonveg_breakfast = Meal.objects(id__nin=assignedMealIds, foodPreference__in=['Non-Vegetarian'],
                                    course__in=['Breakfast'],
                                    avoidableMedCond__ne=usersMedicalCondition)[:nonveg_plan_count['Breakfast']]
    nonveg_lunch = Meal.objects(id__nin=assignedMealIds, foodPreference__in=['Non-Vegetarian'], course__in=['Lunch'],
                                avoidableMedCond__ne=usersMedicalCondition)[:nonveg_plan_count['Lunch']]
    nonveg_dinner = Meal.objects(id__nin=assignedMealIds, foodPreference__in=['Non-Vegetarian'], course__in=['Dinner'],
                                 avoidableMedCond__ne=usersMedicalCondition)[:nonveg_plan_count['Dinner']]
    nonveg_snacks = Meal.objects(id__nin=assignedMealIds, foodPreference__in=['Non-Vegetarian'], course__in=['Snacks'],
                                 avoidableMedCond__ne=usersMedicalCondition)[:nonveg_plan_count['Snacks']]

    nonveg_meals = list(nonveg_breakfast) + list(nonveg_lunch) + list(nonveg_dinner) + list(nonveg_snacks)
    print("Non-Veg Meals : " + str(len(nonveg_meals)))
    return veg_meals + nonveg_meals


''' Method to assign generated meal plans to user and set expiry'''


def getMeals(userId):
    try:
        user = User.objects(id=userId).get()
        newMealsFlag = False
        assignedMealIds = []
        if user['mealAssigned']:
            for meal in user['mealAssigned']:
                assignedMealIds.append(meal['id'])
        if user and user['mealExpiry']:
            ''' Check for meal plan expiry'''
            tzinf = tz.tz.tzoffset('TZONE', int(user['timeZone']) / 1000)  # creating the user's timezone by
            localCurrentTime = utils.default_tzinfo(datetime.now(), tzinf)  # datetime.now(tz=tzinf)
            # creating local time
            # Check if meal plan has expired
            if localCurrentTime > utils.default_tzinfo(user['mealExpiry'], tzinf):
                newMealsFlag = True
            else:
                try:
                    meals = Meal.objects(id__in=assignedMealIds)
                    return jsonify(meals), status.HTTP_200_OK
                except Exception as e:
                    print('Error while getting meals ' + format(e))
                    return jsonify({'stat': 'Some error occurred'}), status.HTTP_500_INTERNAL_SERVER_ERROR
        else:
            newMealsFlag = True

        # ******* New Meal Assignment Starts Here *******
        if newMealsFlag:
            usersMedicalCondition = user['medicalCondition']
            generated_plan = []
            if user['foodPreference'] == 'Vegan':
                generated_plan = vegan_meals(assignedMealIds, usersMedicalCondition)
                print("Vegan Count : " + str(len(generated_plan)))
            elif user['foodPreference'] == 'Vegetarian':
                generated_plan = vegetarian_meals(assignedMealIds, usersMedicalCondition)
                print("Vege Count : " + str(len(generated_plan)))
            else:
                generated_plan = non_veg_meals(assignedMealIds, usersMedicalCondition)
                print("Non-Veg Count : " + str(len(generated_plan)))

            # ****** Assigning generated plan to the user ******

            tzinf = tz.tz.tzoffset('TZONE', int(user['timeZone']) / 1000)
            localCurrentTime = utils.default_tzinfo(datetime.now(), tzinf)  # datetime.now(tz=tzinf)
            expiryTime = localCurrentTime + timedelta(days=1)
            mealExpiry = utils.default_tzinfo(expiryTime.replace(hour=5, minute=0, second=0, microsecond=0),
                                                      tzinf)
            #user['mealAssigned'] = generated_plan
            user.modify(mealExpiry=mealExpiry,mealAssigned=generated_plan)
            return jsonify(user['mealAssigned']), status.HTTP_200_OK
    except Exception as e:
        print("Error occurred in meal assignment : " + format(e))
        return format(e), status.HTTP_500_INTERNAL_SERVER_ERROR


'''
    Service to filter meals

    -Consider user's medical condition
'''


def filterMeals(type, foodPref, userId):
    try:
        user = User.objects(id=userId).get()
        usersMedicalCondition = user['medicalCondition']
        foodPrefArr = []
        exstMealSrchFlag = False
        srchArr = [type];
        vegLimit = 10;
        nonVegLimit = 0;
        if type == 'Snack' or 'Soup' or 'Juice':
            exstMealSrchFlag = True
        if foodPref == 'Non-Vegetarian' or foodPref == 'None':
            foodPrefArr = ['Vegan', 'Vegetarian']
            vegLimit = 5
            nonVegLimit = 5
        else:
            foodPrefArr = [foodPref]
        if exstMealSrchFlag:
            res = []
            mealAssigned = [meal['id'] for meal in user['mealAssigned']]
            mealQuery = Meal.objects(id__in=mealAssigned, course__in=srchArr)
            res = list(mealQuery)
            return jsonify(res), status.HTTP_200_OK
        else:
            vegQuery = Meal.objects(foodPreference__in=foodPrefArr, course__in=srchArr,
                                    avoidableMedCond__ne=usersMedicalCondition)[:vegLimit]
            if foodPref == 'Non-Vegetarian' or foodPref == 'None':
                nonVegQuery = Meal.objects(foodPreference__in=['Non-Vegetarian'], course__in=srchArr,
                                           avoidableMedCond__ne=usersMedicalCondition)[:nonVegLimit]
                res = list(vegQuery) + list(nonVegQuery)
            else:
                res = vegQuery
            return jsonify(res), status.HTTP_200_OK
    except Exception as e:
        print('Error occurred while filtering : ' + format(e))
        return jsonify({'error': format(e)}), status.HTTP_400_BAD_REQUEST


def getMealsList():
    return jsonify(Meal.objects), status.HTTP_200_OK


def updateMeal(meal_id):
    data = AttrDict(request.get_json())

    try:
        updatedMeal = Meal.objects(id=meal_id).update_one(
            name=data.name,
            foodPreference=data.foodPreference,
            cuisine=data.cuisine,
            dietType=[dt for dt in data.dietType],
            idealMedCond=[imc for imc in data.idealMedCond],
            avoidableMedCond=[amc for amc in data.avoidableMedCond],
            course=data.course,
            calories=data.calories,
            nutritionInfo=data.nutritionInfo,
            ingredients=data.ingredients,
            directions=data.directions,
            photoURL=data.photoURL
        )
        return jsonify(updatedMeal), status.HTTP_200_OK
    except Exception as e:
        return jsonify({'Error': format(e)}), status.HTTP_500_INTERNAL_SERVER_ERROR


def deleteMeal(meal_id):
    try:
        delMeal = Meal.objects(id=meal_id).get()
        delMeal.delete()
        return jsonify({'status': 'Meal deleted successfully'}), status.HTTP_200_OK
    except DoesNotExist as dne:
        return 'Meal not found - {}'.format(dne.with_traceback), status.HTTP_400_BAD_REQUEST
    except Exception as e:
        return jsonify({'Error': format(e)}), status.HTTP_500_INTERNAL_SERVER_ERROR
