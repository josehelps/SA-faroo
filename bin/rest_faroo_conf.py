import splunk.admin as admin
import splunk.entity as en
#from splunk.appserver.mrsparkle.lib.util import make_splunkhome_path

#BASE_DIR = make_splunkhome_path(["etc","apps","SA-faroo"])

CONF_FILE = 'sa-faroo'


class FarooHandler(admin.MConfigHandler):
    '''
    set up supported args
    '''
    def setup(self):
        if self.requestedAction == admin.ACTION_EDIT:
            for arg in ['api_key']:
                self.supportedArgs.addOptArg(arg)
    '''
    Read the initial values of the parameters from the custom file myappsetup.conf
    and write them to the setup screen. 
    If the app has never been set up, uses SA-faroo/default/faroo.conf. 
    If app has been set up, looks at local/faroo/faroo.conf first, then looks at 
    default/faroo.conf only if there is no value for a field in local/faroo.conf
    '''

    def handleList(self, confInfo):
        confDict = self.readConf(CONF_FILE)
        if None != confDict:
            for stanza, settings in confDict.items():
                for key, val in settings.items():
                    if key in ['api_key'] and val in [None, '']:
                        val = ''
                    confInfo[stanza].append(key,val)

    def handleEdit(self, confInfo):
        name = self.callerArgs.id
        args = self.callerArgs
        if self.callerArgs.data['api_key'][0] in [None, '']:
            self.callerArgs.data['api_key'][0] = ''     

        '''
        Since we are using a conf file to store parameters, write them to the [setupentity] stanza
        in SA-faroo/local/faroo.conf  
        '''
        self.writeConf('sa-faroo', 'setupentity', self.callerArgs.data)
            
# initialize the handler
admin.init(FarooHandler, admin.CONTEXT_NONE) 






