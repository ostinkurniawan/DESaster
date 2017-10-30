# -*- coding: utf-8 -*-
"""
Module of classes and functions for input/output related to DESaster.

Classes:
importSingleFamilyResidenceStock

@author: Scott Miles (milessb@uw.edu), Derek Huling
"""
from scipy.stats import uniform, beta, weibull_min
from simpy import FilterStore
from desaster.entities import Household, OwnerHousehold, RenterHousehold, Landlord
from desaster.structures import SingleFamilyResidential, Building
import pandas as pd
import numpy as np

def importSingleFamilyResidenceStock(env, stock_df):
    """Define, populate and return a SimPy FilterStore with SingleFamilyResidential() 
    objects to represent a vacant housing stock.
    
    Keyword Arguments:
    env -- Pointer to SimPy env environment.
    stock_df -- Dataframe with required attributes for each vacant home in
                the stock.
    """
    stock_fs = FilterStore(env)

    for i in stock_df.index:
        stock_fs.put(SingleFamilyResidential(stock_df.loc[i]))

    return stock_fs

def importEntities(env, entities_df, entity_type, building_stock = None, write_story = False):
    """Return list of entities.OwnerHouseholds() objects from dataframe containing
    data describing entities' attributes.

    Keyword Arguments:
    env -- Pointer to SimPy env environment.
    building_stock -- a SimPy FilterStore that acts as an occupied building stock.
    entities_df -- Dataframe row w/ entities' input attributes.
    entity_type -- Indicate class of entity: Household, Owner, OwnerHousehold etc.
    write_story -- Boolean indicating whether to track a entities story.
    """
    # try:
    entities = []
    if entity_type.lower() == 'household':
        # Populate the env with entities from the entities dataframe
        for i in entities_df.index:
            
            if entities_df.iloc[i]['Occupancy'].lower() in ['single family house', 'single family home', 
                                    'single family dwelling', 'single family residence',
                                    'sfr', 'sfh', 'sfd', 'mobile home']:
                
                residence = SingleFamilyResidential(
                                    occupancy = entities_df.iloc[i]['Occupancy'],
                                    tenure = entities_df.iloc[i]['Tenure'],
                                    address = entities_df.iloc[i]['Address'],
                                    longitude = entities_df.iloc[i]['Longitude'],
                                    latitude = entities_df.iloc[i]['Latitude'],
                                    value = entities_df.iloc[i]['Value'],
                                    cost = entities_df.iloc[i]['Monthly Cost'],
                                    area = entities_df.iloc[i]['Area'],
                                    bedrooms = entities_df.iloc[i]['Bedrooms'],
                                    bathrooms = entities_df.iloc[i]['Bathrooms'],
                                    listed = entities_df.iloc[i]['Listed'],
                                    damage_state = entities_df.iloc[i]['Damage State'],
                                    building_stock = building_stock
                                    )
            else:
                raise AttributeError("Specified occupancy type ({0}) associated with entity \'{1}\' not supported. Can't complete import.".format(entities_df.iloc[i]['Occupancy'], entities_df.iloc[i]['Name']))
                return
            
            entity = Household(env, 
                                name = entities_df.iloc[i]['Name'],
                                income = entities_df.iloc[i]['Income'],
                                write_story = write_story,
                                residence = residence
                                )
            
            entities.append(entity)
        return entities
    
    elif entity_type.lower() == 'ownerhousehold' or entity_type.lower() == 'owner household':
        # Populate the env with entities from the entities dataframe
        for i in entities_df.index:
            if entities_df.iloc[i]['Occupancy'].lower() in ['single family house', 'single family home', 
                                    'single family dwelling', 'single family residence',
                                    'sfr', 'sfh', 'sfd', 'mobile home']:                  
                real_property = SingleFamilyResidential(
                                                    occupancy = entities_df.iloc[i]['Occupancy'],
                                                    tenure = entities_df.iloc[i]['Tenure'],
                                                    address = entities_df.iloc[i]['Address'],
                                                    longitude = entities_df.iloc[i]['Longitude'],
                                                    latitude = entities_df.iloc[i]['Latitude'],
                                                    value = entities_df.iloc[i]['Value'],
                                                    cost = entities_df.iloc[i]['Monthly Cost'],
                                                    area = entities_df.iloc[i]['Area'],
                                                    bedrooms = entities_df.iloc[i]['Bedrooms'],
                                                    bathrooms = entities_df.iloc[i]['Bathrooms'],
                                                    listed = entities_df.iloc[i]['Listed'],
                                                    damage_state = entities_df.iloc[i]['Damage State'],
                                                    building_stock = building_stock
                                                    )
                        
            else:
                raise AttributeError("Specified occupancy type ({0}) associated with entity \'{1}\' not supported. Can't complete import.".format(entities_df.iloc[i]['Occupancy'], entities_df.iloc[i]['Name']))
                return
            
            entity = OwnerHousehold(env, 
                                    name = entities_df.iloc[i]['Name'],
                                    income = entities_df.iloc[i]['Income'],
                                    savings = entities_df.iloc[i]['Owner Savings'],
                                    insurance = entities_df.iloc[i]['Owner Insurance'],
                                    credit = entities_df.iloc[i]['Owner Credit'],
                                    real_property = real_property,
                                    write_story = write_story
                                    )

            entity.property.owner = entity  
            building_stock.put(real_property)                              
            entities.append(entity)
        return entities
    elif entity_type.lower() == 'renterhousehold' or entity_type.lower() == 'renter household':
        # Populate the env with entities from the entities dataframe
        for i in entities_df.index:
            if entities_df.iloc[i]['Occupancy'].lower() in ['single family house', 'single family home', 
                                    'single family dwelling', 'single family residence',
                                    'sfr', 'sfh', 'sfd', 'mobile home']:                           
                real_property = SingleFamilyResidential(
                                            occupancy = entities_df.iloc[i]['Occupancy'],
                                            tenure = entities_df.iloc[i]['Tenure'],
                                            address = entities_df.iloc[i]['Address'],
                                            longitude = entities_df.iloc[i]['Longitude'],
                                            latitude = entities_df.iloc[i]['Latitude'],
                                            value = entities_df.iloc[i]['Value'],
                                            cost = entities_df.iloc[i]['Monthly Cost'],
                                            area = entities_df.iloc[i]['Area'],
                                            bedrooms = entities_df.iloc[i]['Bedrooms'],
                                            bathrooms = entities_df.iloc[i]['Bathrooms'],
                                            listed = entities_df.iloc[i]['Listed'],
                                            damage_state = entities_df.iloc[i]['Damage State'],
                                            building_stock = building_stock
                                                        )
            else:
                raise AttributeError("Specified occupancy type ({0}) associated with entity \'{1}\' not supported. Can't complete import.".format(entities_df.iloc[i]['Occupancy'], entities_df.iloc[i]['Name']))
                return                      
            
            landlord = Landlord(env, 
                                        name = entities_df.iloc[i]['Landlord'],
                                        savings = entities_df.iloc[i]['Owner Savings'],
                                        insurance = entities_df.iloc[i]['Owner Insurance'],
                                        credit = entities_df.iloc[i]['Owner Credit'],
                                        real_property = real_property,
                                        write_story = write_story
                                        )
            
            entity = RenterHousehold(env, 
                                        name = entities_df.iloc[i]['Name'],
                                        income = entities_df.iloc[i]['Income'],
                                        savings = entities_df.iloc[i]['Tenant Savings'],
                                        insurance = entities_df.iloc[i]['Tenant Insurance'],
                                        credit = entities_df.iloc[i]['Tenant Credit'],
                                        write_story = write_story,
                                        residence = real_property,
                                        landlord = landlord
                                        )
                    
            entity.landlord.tenant = entity
            entity.landlord.property.owner = entity.landlord
            building_stock.put(real_property)
            entities.append(entity)
            
        return entities
    elif entity_type.lower() == 'landlord':
        # Populate the env with entities from the entities dataframe
        for i in entities_df.index:
            if entities_df.iloc[i]['Occupancy'].lower() in ['single family house', 'single family home', 
                                    'single family dwelling', 'single family residence',
                                    'sfr', 'sfh', 'sfd', 'mobile home']: 
                real_property = SingleFamilyResidential(
                                            occupancy = entities_df.iloc[i]['Occupancy'],
                                            tenure = entities_df.iloc[i]['Tenure'],
                                            address = entities_df.iloc[i]['Address'],
                                            longitude = entities_df.iloc[i]['Longitude'],
                                            latitude = entities_df.iloc[i]['Latitude'],
                                            value = entities_df.iloc[i]['Value'],
                                            cost = entities_df.iloc[i]['Monthly Cost'],
                                            area = entities_df.iloc[i]['Area'],
                                            bedrooms = entities_df.iloc[i]['Bedrooms'],
                                            bathrooms = entities_df.iloc[i]['Bathrooms'],
                                            listed = entities_df.iloc[i]['Listed'],
                                            damage_state = entities_df.iloc[i]['Damage State'],
                                            building_stock = building_stock
                                                        )
                
            else:
                raise AttributeError("Specified occupancy type ({0}) associated with entity \'{1}\' not supported. Can't complete import.".format(entities_df.iloc[i]['Occupancy'], entities_df.iloc[i]['Name']))
                return
                                                        
            entity = Landlord(env, 
                                        name = entities_df.iloc[i]['Landlord'],
                                        savings = entities_df.iloc[i]['Owner Savings'],
                                        insurance = entities_df.iloc[i]['Owner Insurance'],
                                        credit = entities_df.iloc[i]['Owner Credit'],
                                        real_property = real_property,
                                        write_story = write_story
                                        )
            
            entity.property.owner = entity
            building_stock.put(real_property)
            entities.append(entity)                                            
        return entities
    else:
        raise AttributeError("Entity type ({0}) not recognized. Can't complete import.".format(entity_type))
        return
    # except:
    #     warnings.showwarning('importEntities: Unexpected missing attribute. Attribute value set to None.',
    #                             DeprecationWarning, filename = sys.stderr,
    #                             lineno=312)

def output_summary(entities, entity_type):
    """ A band-aid function for printing out simulation outputs for entities
    
    """
    if entity_type.lower() in ['ownerhousehold', 'owner household']:
        num_damaged = 0
        num_rebuilt = 0
        num_gave_up_funding_search = 0
        num_home_buy_get = 0
        num_home_buy_put = 0
        num_home_rent_get = 0
        num_home_rent_put = 0
        num_gave_up_home_buy_search = 0
        num_gave_up_home_rent_search = 0
        num_vacant_fixed = 0

        for household in entities:
            if household.residence.damage_state_start != None: num_damaged += 1
            if household.repair_get != None: num_rebuilt += 1
            if household.gave_up_funding_search: num_gave_up_funding_search += 1
            if household.home_buy_put != None: num_home_buy_put += 1
            if household.home_buy_get != None: num_home_buy_get += 1
            if household.home_rent_put != None: num_home_buy_put += 1
            if household.home_rent_get != None: num_home_buy_get += 1
            if household.gave_up_home_buy_search: num_gave_up_home_buy_search += 1
            if household.gave_up_home_rent_search: num_gave_up_home_rent_search += 1

        print('{0} out of {1} owners suffered damage to their homes.\n'.format(num_damaged, len(entities)),
          '{0} out of {1} owners rebuilt or repaired their damaged home.\n'.format(num_rebuilt, len(entities)),
            '{0} out of {1} owners gave up searching for money.\n'.format(num_gave_up_funding_search, len(entities)),
          '{0} out of {1} owners searched to buy a new home.\n'.format(num_home_buy_put, len(entities)),
            '{0} out of {1} owners bought a new home.\n'.format(num_home_buy_get, len(entities)),
            '{0} out of {1} owners searched to temporarily rent a new home.\n'.format(num_home_rent_put, len(entities)),
              '{0} out of {1} owners rented a temporary home.\n'.format(num_home_rent_get, len(entities)),
            '{0} out of {1} owners gave up searching to buy a home.'.format(num_gave_up_home_buy_search, len(entities)),
            '{0} out of {1} owners gave up searching to rent a temporary home.'.format(num_gave_up_home_rent_search, len(entities))
            )
            
    if entity_type.lower() in ['renterhousehold', 'renter household']:
        num_damaged = 0
        num_rebuilt = 0
        num_relocated = 0
        num_displaced = 0
        num_gave_up_funding_search = 0
        num_gave_up_home_search = 0
        num_vacant_fixed = 0

        for renter in entities:
            if renter.landlord.property.damage_state != None: num_damaged += 1
            if renter.landlord.repair_get != None: num_rebuilt += 1
            if renter.landlord.gave_up_funding_search != None: num_gave_up_funding_search += 1
            if not renter.residence: num_displaced += 1
            if renter.gave_up_home_search: num_displaced += 1

        print('{0} out of {1} renters\' homes suffered damage.\n'.format(num_damaged, len(entities)),
              '{0} out of {1} renters\' damaged home was rebuilt or repaired.\n'.format(num_rebuilt, len(entities)),
              '{0} out of {1} renters\' were displaced.\n'.format(num_displaced, len(entities)),
              '{0} landlords gave up searching for repair money.'.format(num_gave_up_funding_search)
             )

def households_to_df(entities):
    """
    
    *** This works but is a bandaid for saving simulation outputs 
    for external visualization or stats. 
    
    *** Eventually add an option so can recursively flatten each prior residence
    
    """
    column_list = []

    for entity in entities: #loop through all entities
        new_column={}
        
        # Create list of residence attributes. Delete attributes that are lists themselves.
        entity_attributes = list(vars(entities[0]).keys()) #gets all potential column names
        entity_attributes.remove('residence')
        entity_attributes.remove('prior_residences')
        entity_attributes.remove('env')
        entity_attributes.remove('write_story')

        # Catch exception. RenterHousehold won't have property.
        try:
            entity_attributes.remove('property')
            entity_attributes.remove('prior_properties')
        except ValueError:
            pass
        
        #loop through the entity-level attributes and assign to new column
        for attribute in entity_attributes: 
            try:
                new_column[attribute] = entity.__getattribute__(attribute)      
            except ValueError:
                new_column[attribute] = np.nan
            except AttributeError as e:
                new_column[attribute] = np.nan
                print("Household {0} had an attribrute error, {1}".format(entity.name, e))
        
        # Create list of residence attributes. Delete attributes that are lists themselves.
        residence_attributes = list(vars(entities[0].residence).keys()) #gets all potential column names
        residence_attributes.remove('owner')
        residence_attributes.remove('stock')

        #loop through the residence-level attributes and assign to new column
        for attribute in residence_attributes: 
            try:
                new_column[attribute] = entity.prior_residences[0].__getattribute__(attribute)      
            except IndexError:
                new_column[attribute] = entity.residence.__getattribute__(attribute) 
            except AttributeError as e:
                new_column[attribute] = np.nan
                print("Household {0} had an attribrute error, {1}".format(entity.name, e))

        #Appen newly made column to column list
        column_list.append(new_column)
    
    # Create and return dataframe from list of attribute columns
    return pd.DataFrame(column_list)