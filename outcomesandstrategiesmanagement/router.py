class OASMRouter(object):
    '''
    A router to control all database operations on models
    in the outcomesandstrategiesmanagement application.
    '''
    def db_for_read(self,model,**hints):
        '''
        Attemps to read outcomesandstrategiesmanagement models
        go to outcomesandstrategiesmanagement_db.
        '''
        if model._meta.app_label == 'outcomesandstrategiesmanagement':
            return 'outcomesandstrategiesmanagement_db'
        return None
    
    def db_for_write(self,model,**hints):
        '''
        Attempts to write outcomesandstrategiesmanagement models
        go to outcomesandstrategiesmanagement_db.
        '''
        if model._meta.app_label == 'outcomesandstrategiesmanagement':
            return 'outcomesandstrategiesmanagement_db'
        return None
    
    def allow_relation(self,obj1,obj2,**hints):
        '''
        Allow relations if a model in the 
        outcomesandstrategiesmanagement app is involved.
        '''
        if obj1._meta.app_label == 'outcomesandstrategiesmanagement' or \
           obj2._meta.app_label == 'outcomesandstrategiesmanagement':
            return True
        return None
    
    def allow_syncdb(self,db,model):
        '''
        Make sure the outcomesandstrategiesmanagement app 
        only appears in outcomesandstrategiesmanagement_db.
        '''
        if db == 'outcomesandstrategiesmanagement_db':
            return model._meta.app_label == 'outcomesandstrategiesmanagement'
        elif model._meta.app_label == 'outcomesandstrategiesmanagement':
            return False
        return None