# -*- coding: utf-8 -*-
"""
Created on July 2016

@author: Scott

processes related to rebuilding
"""
from desaster.config import building_repair_times
from desaster import request
from simpy import Interrupt
import random

def home(simulation, human_capital, entity, write_story = True, callbacks = None): 
    try: # in case a process interrupt is thrown in a master process
        

        # With a permit and enough money, can rebuild
        if entity.permit_get > 0.0 and entity.money_to_rebuild >= entity.residence.damage_value:
            # Put in request for contractors to repair house
            entity.house_put = simulation.now

            contractors_request = human_capital.contractors.request()
            yield contractors_request
            
            # Get the rebuild time for the entity from config.py 
            # which imports the HAZUS repair time look up table.
            # Rebuild time is based on occupancy type and damage state.
            rebuild_time = building_repair_times.ix[entity.residence.occupancy][entity.residence.damage_state]
            
            yield simulation.timeout(rebuild_time)
        
            human_capital.contractors.release(contractors_request)
            
            entity.residence.damage_state = 'None'
            entity.residence.damage_value = 0.0

            # Record time when household gets house
            entity.house_get = simulation.now
            
            if write_story == True:
                # Write the household's story
                entity.story.append(
                    'The house was rebuilt {0} days after the event, taking {1} days to rebuild. '.format(
                    entity.house_get, entity.house_get - entity.house_put))
        
        elif entity.money_to_rebuild < entity.residence.damage_value:
            if story == True:
                entity.story.append(
                    '{0} was unable to get enough money to rebuild. '.format(
                    entity.name))
        else: 
            if write_story == True:
                entity.story.append(
                    '{0} was unable to get a permit to rebuild. '.format(
                    entity.name))

    except Interrupt as i: # Handle any interrupt thrown by a master process
        if write_story == True:
            #If true, write their story
            entity.story.append(
                    '{0} gave up {1} days into the home rebuilding process. '.format(
                    entity.name, i.cause))
    
    if callbacks is not None:
        yield simulation.process(callbacks)

    else:
        pass
        
def stock(simulation, structure_stock, fix_probability, fix_schedule, human_capital):
    random.seed(simulation.now)
    
    yield simulation.timeout(fix_schedule)
    # 
    # 
    # Find a new home from the vacant housing stock with similar attributes as current home
    structures_list = []
    
    for structure in structure_stock.items:
        print(structure.address, structure.damage_state)
    
        fix_structure = yield structure_stock.get(lambda getStructure: 
                                                        getStructure.value > 0.0
                                                )
        fix_structure.damage_state = 'None'
        structures_list.append(fix_structure)                                  
    
    for structure in structures_list:
        print(fix_structure.address, fix_structure.damage_state)
        structure_stock.put(fix_structure)
        
    #     
    #     
        # if stock.items[i].inspected == True and \
        # (stock.items[i].damage_state == 'Moderate' or stock.items[i].damage_state == 'Moderate'):
        # 
        #     if random.uniform(0, 1.0) <= fix_probability:
        #         print('Gonna fix it!')
        #         contractors_request = human_capital.contractors.request()
        #         yield contractors_request
        #        
        #         # Get the rebuild time for the entity from config.py 
        #         # which imports the HAZUS repair time look up table.
        #         # Rebuild time is based on occupancy type and damage state.
        #         rebuild_time = building_repair_times.ix[stock.items[i].occupancy][stock.items[i].damage_state]
        #        
        #         yield simulation.timeout(rebuild_time)
        #    
        #         human_capital.contractors.release(contractors_request)
        #         
        #         print(stock.items[i].damage_state)
        #         stock.items[i].damage_state = 'None'
        #         print(stock.items[i].damage_state)
        #         stock.items[i].damage_value = 0.0