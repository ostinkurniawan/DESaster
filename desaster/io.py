# -*- coding: utf-8 -*-
"""
Module of classes and functions for input/output related to DESaster.

Classes:
importSingleFamilyResidenceStock

@author: Scott Miles (milessb@uw.edu), Derek Huling
"""
from scipy.stats import uniform, beta, weibull_min
from simpy import FilterStore
from desaster.entities import Household, OwnerHousehold, RenterHousehold, Landlord, Owner
from desaster.structures import ResidentialBuilding, Building
import pandas as pd
import numpy as np

def importResidentialBuildingStock(env, stock_df, stock_fs, write_story = False):
    """Define, populate and return a SimPy FilterStore with ResidentialBuilding() 
    objects to represent a vacant housing stock.
    
    Keyword Arguments:
    env -- Pointer to SimPy env environment.
    stock_df -- Dataframe with required attributes for each vacant building in
                the stock.
    stock_fs -- Empty Simpy FilterStore to import buildings into.
    """
    for row in stock_df.itertuples():
        
        building = ResidentialBuilding(
                                    occupancy = row.occupancy,
                                    tenure = row.tenure,
                                    address = row.address,
                                    longitude = row.longitude,
                                    latitude = row.latitude,
                                    value = row.value,
                                    monthly_cost = row.monthly_cost,
                                    move_in_cost = row.move_in_cost,
                                    area = row.area,
                                    bedrooms = row.bedrooms,
                                    bathrooms = row.bathrooms,
                                    listed = row.listed,
                                    damage_state = row.damage_state,
                                    building_stock = stock_fs
                                    )
                                
        if row.tenure in ['rental', 'Rental', 'hotel', 'Hotel']:
            try:
                owner = Landlord(env, 
                         name = row.owner,
                         savings = row.owner_savings, 
                        insurance = row.owner_insurance,
                         credit = row.owner_credit,
                        tenant = None,
                         write_story = write_story)
            except AttributeError:
                owner = Landlord(env, 
                         name = 'Unspecified',
                         write_story = write_story)
            
            
        else:
            try:
                owner = Owner(env, 
                         name = row.owner,
                         savings = row.owner_savings, 
                        insurance = row.owner_insurance,
                         credit = row.owner_credit,
                         write_story = False)
            except AttributeError:
                owner = Owner(env, 
                            name = 'Unspecified',
                            write_story = write_story)
                
            owner.real_property = building
            building.owner = owner
        
        owner.real_property = building
        building.owner = owner
        
        stock_fs.put(building)
    
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
        for row in entities_df.itertuples():
            
            if row.occupancy.lower() in ['single family house', 'single family home', 
                                    'single family dwelling', 'single family residence',
                                    'sfr', 'sfh', 'sfd', 'mobile home']:
                
                residence = ResidentialBuilding(
                                    occupancy = row.occupancy,
                                    tenure = row.tenure,
                                    address = row.address,
                                    longitude = row.longitude,
                                    latitude = row.latitude,
                                    value = row.value,
                                    monthly_cost = row.monthly_cost,
                                    move_in_cost = row.move_in_cost,
                                    area = row.area,
                                    bedrooms = row.bedrooms,
                                    bathrooms = row.bathrooms,
                                    listed = row.listed,
                                    damage_state = row.damage_state,
                                    building_stock = building_stock
                                    )
            else:        
                raise AttributeError("Specified occupancy type ({0}) associated with entity \'{1}\' not supported. Can't complete import.".format(row.occupancy, row.name))
                return
            
            entity = Household(env, 
                                name = row.owner,
                                income = row.owner_income,
                                write_story = write_story,
                                residence = residence
                                )
            
            entities.append(entity)
        return entities
    
    elif entity_type.lower() == 'ownerhousehold' or entity_type.lower() == 'owner household':
        # Populate the env with entities from the entities dataframe
        for row in entities_df.itertuples():
            if row.occupancy.lower() in ['single family house', 'single family home', 
                                    'single family dwelling', 'single family residence',
                                    'sfr', 'sfh', 'sfd', 'mobile home']:                  
                real_property = ResidentialBuilding(
                                                    occupancy = row.occupancy,
                                                    tenure = row.tenure,
                                                    address = row.address,
                                                    longitude = row.longitude,
                                                    latitude = row.latitude,
                                                    value = row.value,
                                                    monthly_cost = row.monthly_cost,
                                                    move_in_cost = row.move_in_cost,
                                                    area = row.area,
                                                    bedrooms = row.bedrooms,
                                                    bathrooms = row.bathrooms,
                                                    listed = row.listed,
                                                    damage_state = row.damage_state,
                                                    building_stock = building_stock
                                                    )
                        
            else:
                raise AttributeError("Specified occupancy type ({0}) associated with entity \'{1}\' not supported. Can't complete import.".format(row.occupancy, row.name))
                return
            
            entity = OwnerHousehold(env, 
                                    name = row.owner,
                                    income = row.owner_income,
                                    savings = row.owner_savings,
                                    insurance = row.owner_insurance,
                                    credit = row.owner_credit,
                                    real_property = real_property,
                                    write_story = write_story
                                    )

            entity.property.owner = entity  
            building_stock.put(real_property)                              
            entities.append(entity)
        return entities
    elif entity_type.lower() == 'renterhousehold' or entity_type.lower() == 'renter household':
        # Populate the env with entities from the entities dataframe
        for row in entities_df.itertuples():
            if row.occupancy.lower() in ['single family house', 'single family home', 
                                    'single family dwelling', 'single family residence',
                                    'sfr', 'sfh', 'sfd', 'mobile home']:                           
                real_property = ResidentialBuilding(
                                            occupancy = row.occupancy,
                                            tenure = row.tenure,
                                            address = row.address,
                                            longitude = row.longitude,
                                            latitude = row.latitude,
                                            value = row.value,
                                            monthly_cost = row.monthly_cost,
                                            move_in_cost = row.move_in_cost,
                                            area = row.area,
                                            bedrooms = row.bedrooms,
                                            bathrooms = row.bathrooms,
                                            listed = row.listed,
                                            damage_state = row.damage_state,
                                            building_stock = building_stock
                                                        )
            else:
                raise AttributeError("Specified occupancy type ({0}) associated with entity \'{1}\' not supported. Can't complete import.".format(row.occupancy, row.name))
                return                      
            
            landlord = Landlord(env, 
                                        name = row.owner,
                                        savings = row.owner_savings,
                                        insurance = row.owner_insurance,
                                        credit = row.owner_credit,
                                        real_property = real_property,
                                        write_story = write_story
                                        )
            
            entity = RenterHousehold(env, 
                                        name = row.tenant,
                                        income = row.tenant_income,
                                        savings = row.tenant_savings,
                                        insurance = row.tenant_insurance,
                                        credit = row.tenant_credit,
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
        for i in entities_df.itertuples():
            if row.occupancy.lower() in ['single family house', 'single family home', 
                                    'single family dwelling', 'single family residence',
                                    'temporary lodging', 'sfr', 'sfh', 'sfd', 'mobile home']: 
                real_property = ResidentialBuilding(
                                            occupancy = row.occupancy,
                                            tenure = row.tenure,
                                            address = row.address,
                                            longitude = row.longitude,
                                            latitude = row.latitude,
                                            value = row.value,
                                            monthly_cost = row.monthly_cost,
                                            move_in_cost = row.move_in_cost,
                                            area = row.area,
                                            bedrooms = row.bedrooms,
                                            bathrooms = row.bathrooms,
                                            listed = row.listed,
                                            damage_state = row.damage_state,
                                            building_stock = building_stock
                                                        )
                
            else:
                raise AttributeError("Specified occupancy type ({0}) associated with entity \'{1}\' not supported. Can't complete import.".format(row.occupancy, row.name))
                return
                                                        
            entity = Landlord(env, 
                                        name = row.owner,
                                        savings = row.owner_savings,
                                        insurance = row.owner_insurance,
                                        credit = row.owner_credit,
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
        num_homeless = 0

        for household in entities:
            if len(household.prior_properties) == 0:
                if household.property.damage_state_start != 'None': num_damaged += 1
            else:
                if household.prior_properties[0].damage_state_start != 'None': num_damaged += 1
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
            '{0} out of {1} owners gave up searching to rent a temporary home.'.format(num_gave_up_home_rent_search, len(entities)),
            '{0} out of {1} owners are homeless.\n'.format(num_homeless, len(entities)),
            )
            
    if entity_type.lower() in ['renterhousehold', 'renter household']:
        num_damaged = 0
        num_rebuilt = 0
        num_relocated = 0
        num_homeless = 0
        num_gave_up_funding_search = 0
        num_gave_up_home_search = 0
        num_vacant_fixed = 0

        for renter in entities:
            if renter.landlord.property.damage_state_start != 'None': num_damaged += 1
            if renter.landlord.repair_get != None: num_rebuilt += 1
            if renter.landlord.gave_up_funding_search != None: num_gave_up_funding_search += 1
            if not renter.residence: num_displaced += 1
            if len(renter.prior_residences) > 0: num_relocated += 1
            if not renter.residence: num_homeless += 1

        print('{0} out of {1} renters\' homes suffered damage.\n'.format(num_damaged, len(entities)),
              '{0} out of {1} renters are homeless.\n'.format(num_homeless, len(entities)),
              '{0} out of {1} renters relocated.\n'.format(num_relocated, len(entities)),
            '{0} out of {1} landlords\' damaged property was rebuilt or repaired.\n'.format(num_rebuilt, len(entities)),
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
        if 'landlord' in entity_attributes: 
            entity_attributes.remove('landlord')

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
                print("Household residence {0} had an attribrute error, {1}".format(entity.name, e))

        #Appen newly made column to column list
        column_list.append(new_column)
    
    # Create and return dataframe from list of attribute columns
    return pd.DataFrame(column_list)