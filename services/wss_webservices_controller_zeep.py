from zeep import Client, AsyncClient
from zeep.transports import Transport, AsyncTransport
from zeep.plugins import HistoryPlugin
from requests import Session
from requests.auth import HTTPBasicAuth
import xmltodict
from lxml import etree
from loguru import logger
import yaml
import httpx



# Urllib3 Disable Warnings
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Import Security data
with open(r'config/config.yaml', encoding='utf8') as f:
    config = yaml.safe_load(f)

def parse_content(content):
    """-"""
    data = xmltodict.parse(content)
    print(data)


class WssZeep():
    """
    This is main class for providing communication with the WSS WebServices
    """

    def __init__(self, end_point= None, async_client=False):
        if end_point is None:
            end_point = config['accept_solution']['end_point']
        self.end_point = end_point
        self.user_name = config['accept_solution']['user_name']
        self.user_pswd = config['accept_solution']['user_pswd']
        self.history = HistoryPlugin()
        self.async_client = async_client
        self.client = None
        self.factory = None

        if self.async_client is True:
            httpx_client = httpx.AsyncClient(verify=False,
                                             auth=(self.user_name, self.user_pswd),
                                             )
            self.client = AsyncClient(self.end_point,
                                           transport=AsyncTransport(client=httpx_client))
        else:
            session = Session()
            session.auth = HTTPBasicAuth(self.user_name, self.user_pswd)
            session.verify = False
            self.history = HistoryPlugin()
            self.client = Client(self.end_point,
                            transport=Transport(session=session),
                            plugins=[self.history]
                            )
   
        # Try to initialize the factory for SVC or for ASMX
        try:
            self.factory = self.client.type_factory('ns2')  # SVC
        except ValueError:
            self.factory = self.client.type_factory('ns0')  # ASMX

    def get_raw_xml(self,
                    method:str,
                    parameters=None):
        """
        Generate raw XML

        """
        xml_str = ''
        try:
            node = self.client.create_message(self.client.service,
                                              method,
                                              parameters)
            xml_str = etree.tostring(node, pretty_print=True).decode()
        except BaseException as base_exception:
            logger.info(base_exception)
        return xml_str

    def get_base_document_field(self, name:str, value:str):
        """
        Generate DocumentField for WSS WebServices

        Args:
            name (str): Name of the field
            value (str): Value for the field

        Returns:
            Dict: DocumentField for WSS WebServices
        """
        # Try to initialize the factory for SVC or for ASMX
        try:
            df_type = self.client.get_type('ns2:DocumentField')
        except ValueError:
            df_type = self.client.get_type('ns0:DocumentField')
        document_field = df_type(Name=name, Value=value)
        return document_field

    def get_lookup_document_field(self, name:str, search_field:str, value:str):
        """
        Generate DocumentLookupField for WSS WebServices

        Args:
            name (str): Name of field(system)
            search_field (str): Name of field for LookUp list search
            value (str): Value for LookUp field search

        Returns:
            zeep_object: DocumentLookupField for WSS WebServices
        """
        # Try to initialize the factory for SVC or for ASMX
        try:
            df_type = self.client.get_type('ns2:DocumentLookupField')
        except ValueError:
            df_type = self.client.get_type('ns0:DocumentLookupField')
        document_field = df_type(Name=name, SearchField=search_field, Value=value)
        return document_field

    def get_file_document_field(self, field_name:str,
                                  file_name:str, base64_str:str):
        """Generate DocumentFilesField for WSS WebServices

        Args:
            field_name (str): Name of field
            file_name (str): Name of file
            base64_str (str): File content in base64 format

        Returns:
            _type_: _description_
        """

        base64_str=base64_str.encode('UTF-8')

        # Try to initialize the factory for SVC or for ASMX
        try:
            df_type = self.client.get_type('ns2:DocumentFilesField')
        except ValueError:
            df_type = self.client.get_type('ns0:DocumentFilesField')

        try:
            if_type = self.client.get_type('ns2:ItemFile')
        except ValueError:
            if_type = self.client.get_type('ns0:ItemFile')

        file_data = if_type(Content=base64_str, Name=file_name)
        file_field = df_type(Name=field_name, Files=file_data)
        return file_field

    def get_param_get_document_by_fields(self,
                               list_name: str = 'Users',
                               user_mail: str = 'test2@wss-consulting.ru',
                               searchable_field: dict = None
                               ):
        """
        Generate 'document' for soap request

        Args:
            client (Client): zeep client

            list_name (str, optional): The NAME of list in which the search will be performed.
            Defaults to 'Users'.

            user_mail (str, optional): UserMail from what name will the search be performed.
            Defaults to 'test2@wss-consulting.ru'.

            searchable_field (dict, optional): {FieldName: SearchValue}.
            Defaults to { 'Имя пользователя': 'Кижапкина Елена' }.
        """

        if searchable_field is None:
            searchable_field = {
                'Имя пользователя': 'Кижапкина Елена'
                }

        factory = self.factory

        # Generete list of search parameters [Value, Data] for SearchableField
        searchable_field_list = self.dict_to_searchable_field_list(factory,
                                                              searchable_field)

        # Generate parameters body
        param = factory.SearchParameters(
            Fields = factory.ArrayOfSearchableField(
                SearchableField = searchable_field_list
            ),
            ListName = list_name,
            UserMail = user_mail
        )

        return param

    def get_param_accept_document_solution(self,
                                           comment_to_solution: str = None,
                                           emails_to_notify: str = None,
                                           reg_number: str = None,
                                           solution: str = None,
                                           user_email: str = None,
                                           base_fields:list = None,
                                        #    files_files:list = None,
                                           ):
        """Generate parameters for AcceptDocumentRequestParameters (method WSS Webserives)

        Args:
            comment_to_solution (str, optional): Comment to solution. Defaults to None.
            emails_to_notify (str, optional): To whom the message will be sent. Defaults to None.
            reg_number (str, optional): RegNumber of documents in the WssDocs. Defaults to None.
            solution (str, optional): System name of solution which will be used. Defaults to None.
            user_email (str, optional): On whose behalf accept solution. Defaults to None.
            base_fields (list, optional): ns2:DocumentField structure
                can be generate by get_base_document_field. Defaults to None.
            files_files (list, optional): ns2:DocumentFilesField  # Don't work. Defaults to None.
            lookup_fields (list, optional): ns2:DocumentLookupField  # Don't work. Defaults to None.

        Returns:
            ZeepObject: Structure of data for WssZeep
        """

        # Set the default value to the variable
        if comment_to_solution is None:
            comment_to_solution = 'Тестовый комментарий'
        if emails_to_notify is None:
            emails_to_notify = config['web_service']['test_email']
        if reg_number is None:
            reg_number = 'Пр-ТК-2021-0003'
        if solution is None:
            solution = 'Разослать'
        if user_email is None:
            user_email = config['web_service']['test_email'] 

        factory = self.factory

        # Generate parameters body
        param = factory.AcceptDocumentRequestParameters(
            CommentToSolution = comment_to_solution,
            # DocumentFields=[{'BaseDocumentField':[df,df2]},],
            DocumentFields=[{'BaseDocumentField':base_fields}],
            Emails = emails_to_notify,
            RegNumber = reg_number,
            SolutionName = solution,
            User = user_email
        )

        return param

    def get_param_create_document(self,
                                  doc_type:str,
                                  user_email:str,
                                  base_fields:list = None,
                                  ):

        factory = self.factory

        param = factory.RequestParameters(
           AgreementInfo='',
           DocType=doc_type,
           DocumentFiles='',
           FieldValues=[{'BaseDocumentField':base_fields}],
           UserMail=user_email
        )

        return param

    def send_request(self,
                     method_str,
                     param):
        """
        Spend request to WebServices and try catch Error

        Args:
            method_str (str): Name one of the available methods:
                AcceptDocumentSolution,
                CreateDocument,
                CreateElement,
                FindObjects,
                GetDocumentsByFields,
                GetFile,
                UpdateElement,
            param (dict): Structure of parameters of wsszeep for web services
        """
        client = self.client
        return_result = True

        factory_method = {
            'AcceptDocumentSolution' : client.service.AcceptDocumentSolution,
            'CreateDocument': client.service.CreateDocument,
            'CreateElement': client.service.CreateElement,
            'FindObjects': client.service.FindObjects,
            'GetDocumentsByFields': client.service.GetDocumentsByFields,
            'GetFile': client.service.GetFile,
            'UpdateElement': client.service.UpdateElement
        }

        if method_str in factory_method and param is not None:
            method = factory_method[method_str]
            try:
                result = method(param)
            except ConnectionError:
                logger.info('ConnectionError')
                return_result = False

            error = self.check_result(result)
            if error:
                logger.info(error)
                return_result = False

        else:
            logger.info('Incorrect params')
            return_result = False

        return return_result

    def find_objects(self,
                     client:Client,
                     start_date:str = '2020-11-18T23:59:59',
                     end_date:str = '2020-11-18T00:00:00',
                     ais_number:str = 'ТО02КО0200001187'
                    ):
        """
        # ? Need to test
        """

        try:
            factory = client.type_factory('ns4')
        except ValueError:
            factory = client.type_factory('ns0')

        param = factory.SearchObjectsRequestParameters(
        StartDate = start_date,
        EndDate = end_date,
        AISNumber = ais_number
        )

        return param

    def dict_to_searchable_field_list(self, factory, dict_value:dict):
        '''
        Change structure data by dict to list format [Name:{name}, Value:{value}]
        '''
        result = []
        keys = dict_value.keys()

        for key in keys:
            result.append(factory.SearchableField(Name = key, Value = dict_value[key]))

        return result

    def check_result(self, result):
        '''
        Check result from Zeep
        If return None all is good
        Or It's error msg
        '''
        if result is None:
            return result

        #? There are Result and OperationResult in result, but i just skip parse it

        error = 'Can\'t parse result from Zeep'

        try:
            error = result.ErrorMessage
        except AttributeError:
            pass

        try:
            error = result.ErrorText
        except AttributeError:
            pass

        return error

    def print_history(self):
        """
        Print last request and response. This function only for debug
        """
        try:
            for hist in [self.history.last_sent, self.history.last_received]:
                print(etree.tostring(hist["envelope"], encoding="unicode", pretty_print=True))
        except (IndexError, TypeError):
            # catch cases where it fails before being put on the wire
            pass

    def pares_last_response(self):
        """
        # ! Don't work
        """
        try:
            data = xmltodict.parse(self.history.last_received)
            print(data)
        except (IndexError, TypeError):
            # catch cases where it fails before being put on the wire
            logger.info('None')

def test_1():
    """Test work on WssDocs"""
    wsszeep = WssZeep()
    bdf = wsszeep.get_base_document_field('Содержание','Здесь был тест')
    param = wsszeep.get_param_accept_document_solution(
        comment_to_solution = '',
        emails_to_notify='',
        reg_number='',
        solution='',
        user_email = '',
        base_fields=[bdf])
    zeep_result = wsszeep.send_request('AcceptDocumentSolution', param)
    logger.info(zeep_result)
    # wsszeep.print_history()
    # wsszeep.pares_last_response()


def main():
    """
    Main function for test class

    Available methods:
        AcceptDocumentSolution
        CreateDocument
        CreateElement
        FindObjects
        GetDocumentsByFields
        GetFile
        UpdateElement

    1) Create wsszeep client:
        wsszeep = WssZeep()

    2) Create param for one of the methods (example GetDocumentsByFields):
        param = wsszeep.get_param_get_document_by_fields()

        2.1) Some methods need to specify parameters:
            DocumentField, DocumentFilesField, DocumentLookupField
            You can get it for special method:


    3) CHOOSE:
        -- create Raw XML:
            xml = wsszeep.get_raw_xml('GetDocumentsByFields', param)

        -- Spend request and parse response:
            wsszeep.send_request('GetDocumentsByFields', param)
            wsszeep.print_history()
            wsszeep.pares_last_response()
    """
    # wsszeep = WssZeep()
    # param = wsszeep.get_param_get_document_by_fields()

    # example how generate Raw XML request
    # xml = wsszeep.get_raw_xml('GetDocumentsByFields', param)
    # print(xml)

    # Example how use WebServices
    # wsszeep.send_request('GetDocumentsByFields', param)
    # wsszeep.print_history()
    # wsszeep.pares_last_response()

    # df = wsszeep.get_base_document_field(name='Содержани', value='qaz')
    # param = wsszeep.get_param_accept_document_solution(base_fields=[df])
    # xml = wsszeep.get_raw_xml('AcceptDocumentSolution', parameters=param)
    # print(xml)

    # TEST WORK
    test_1()




if __name__ == '__main__':
    main()
    # print(config['accept_solution'])
