#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
from xml.etree import ElementTree
from loguru import logger
import re
from typing import Optional

import yaml
with open(r'config/config.yaml', encoding='utf8') as f:
    config = yaml.safe_load(f)

namespace_for_etree = {
    's': 'http://schemas.xmlsoap.org/soap/envelope',
    'a': 'http://schemas.datacontract.org/2004/07/WSSC.V4.DMS.EKV.WssDocsService',
    'c': 'http://schemas.datacontract.org/2004/07/WSSC.V4.DMS.EKV.WssDocsService.CreateElementObjectModel',
    'u': 'http://schemas.datacontract.org/2004/07/WSSC.V4.DMS.EKV.WssDocsService.UpdateElementObjectMode',
    'i': 'http://www.w3.org/2001/XMLSchema-instance'
}


def post(endpoint=None, body=None, method=None):
    """
    :param endpoint: str -> URL to WSDL
    :param body: str -> XML code for request
    :param method: str -> method name need for header
    :return:
    """

    if endpoint is None:
        endpoint = 'https://wssdocs.vostok-electra.ru/ekv/WssDocsService.svc?wsdl'
    if body is None:
        body = """<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:tem="http://tempuri.org/" xmlns:wssc="http://schemas.datacontract.org/2004/07/WSSC.V4.DMS.EKV.WssDocsService">
       <soapenv:Header/>
       <soapenv:Body>
          <tem:GetDocumentsByFields>
             <tem:parameters>
                <wssc:Fields>
                   <wssc:SearchableField>
                      <wssc:Name>Имя пользователя</wssc:Name>
                      <wssc:Value>AAAАлександров Д</wssc:Value>
                   </wssc:SearchableField>
                </wssc:Fields>
                <wssc:ListName>Users</wssc:ListName>
                <wssc:UserMail>test2@wss-consulting.ru</wssc:UserMail>
             </tem:parameters>
          </tem:GetDocumentsByFields>
       </soapenv:Body>
    </soapenv:Envelope>"""
    if method is None:
        method = 'GetDocumentsByFields'

    body = body.encode('utf-8')
    session = requests.session()

    session.headers = {
        "Accept-Encoding": "gzip,deflate",
        "Content-Type": "text/xml;charset=UTF-8",
        "SOAPAction": "http://tempuri.org/IWssDocsService/{}".format(method),
        "Connection": "Keep-Alive",
        "User-Agent": "Apache-HttpClient/4.1.1 (java 1.5)",
        "Cookie": "ARRAffinity=30e5a70d60084fdad3ad7f8752b1125bcf96af78317ad48bb45a3175159dbc61",
        "Cookie2": "$Version=1",
        "Authorization":  config['web_service']['base64_auth']
    }

    # POST request
    response = session.post(url=endpoint, data=body, verify=False)
    logger.debug('POST: status_code = {}'.format(response.status_code))

    if response.status_code == 200:
        if parse_response_xml(response):
            return True
        else:
            return False
    else:
        return False


def get_value_xml_elem(tree, elem_list, name):
    """
    Looking for value of element by name in Tree
    :param tree: xml.etree.ElementTree
    :param elem_list: list of element
    :param name:
    :return:
    """
    element_value = None

    try:
        r = re.compile(".*{0}.*".format(name))  # Make regX
        element_name = list(filter(r.match, elem_list))[-1]
    except IndexError:
        logger.debug('TREE: {0} not found'.format(name))

    try:
        element_value = list(tree.iter(element_name))[0].text  # Get result text from xml
    except BaseException as be:
        logger.debug(be)

    return element_value


def parse_response_xml(response: requests.models.Response):
    """Main check result"""
    content = response.content.decode('utf-8')

    # Try get dom
    try:
        tree = ElementTree.fromstring(response.content)
    except BaseException as be:
        logger.info('Get ElementTree: {}'.format(be))

    # Generate list of all elements of Tree from XML
    elem_list = []
    for elem in tree.iter():
        elem_list.append(elem.tag)

    # Looking for elements
    error_text = get_value_xml_elem(tree, elem_list, 'Error')
    oper_result = get_value_xml_elem(tree, elem_list, 'OperationResult')
    main_result = get_value_xml_elem(tree, elem_list, 'Result')

    logger.debug('OR:{} MR:{}'.format(oper_result, main_result))

    if (oper_result == '1' or main_result == '0' or
        oper_result == 'true' or main_result == 'true') and error_text is None:
        return True
    else:
        logger.debug('SOAP request: {0}'.format(content))
        logger.info(error_text)
        return False


def dict_to_xml_body(value):
    """
    Auxiliary function convert dict to xml(str) body
    Only Create
    :param value: dict of Field:Value
    :return: xml(str)
    """
    keys = value.keys()
    xml_body = ''
    for key in keys:
        xml_body += """
                     <wssc1:ItemField>
                        <wssc1:Name>{0}</wssc1:Name>
                        <wssc1:Value>{1}</wssc1:Value>
                     </wssc1:ItemField>""".format(key, value[key])
    return xml_body


def generate_xml_updateitem(item_id, value):
    # Convert dict to xml code for WSDL
    # For Update
    items_field = dict_to_xml_body(value)

    # Generate body for WSDL
    body_request = """
                       <wssc:UpdateItem>
                          <wssc:LookupItemId>{0}</wssc:LookupItemId>
                          <wssc:LookupValue>
                            {1}
                          </wssc:LookupValue>
                       </wssc:UpdateItem>
                       """.format(item_id, items_field)
    return  body_request


def create_element(endpoint, list_id, value):
    """
    Main function for create element
    :param endpoint: Url for wsdl
    :param list_id: ListID for add
    :param value: dict of FieldName:Value
    :return: (bool) True or False
    """

    # Convert dict to xml code for WSDL
    items_field = dict_to_xml_body(value)

    # Generate body for WSDL
    body_request = """
    <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" 
    xmlns:tem="http://tempuri.org/" 
    xmlns:wssc="http://schemas.datacontract.org/2004/07/WSSC.V4.DMS.EKV.WssDocsService.ElementsLogic.CreateElementObjectModel" 
    xmlns:wssc1="http://schemas.datacontract.org/2004/07/WSSC.V4.DMS.EKV.WssDocsService.ObjectModel">
       <soapenv:Header/>
       <soapenv:Body>
          <tem:CreateElement>

             <tem:parameters>
                <wssc:Items>
                   <wssc:ItemsField>
                      <wssc:LookupValue>

                        {0}

                      </wssc:LookupValue>
                   </wssc:ItemsField>
                </wssc:Items>
                
                <wssc:ListID>{1}</wssc:ListID>

             </tem:parameters>
          </tem:CreateElement>
       </soapenv:Body>
    </soapenv:Envelope>""".format(items_field, list_id)
    # print(body_request)

    # Try and check result of POST request
    is_correct = post(endpoint, body_request, 'CreateElement')
    if is_correct:
        logger.info('Result: +')
        return True
    else:
        logger.info('Result: -')
        return False


def update_one_element(endpoint, list_id, item_id, value):
    """
    Main function for update element
    :param endpoint: (str) Url for wsdl
    :param list_id: (int) ListID for add
    :param item_id: (int) ItemID for add
    :param value: (dict) of FieldName:Value
    :return: (bool) True or False
    """

    # Convert dict to xml code for WSDL
    items_field = dict_to_xml_body(value)

    # Generate body for WSDL
    body_request = """
    <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" 
    xmlns:tem="http://tempuri.org/" 
    xmlns:wssc="http://schemas.datacontract.org/2004/07/WSSC.V4.DMS.EKV.WssDocsService.ElementsLogic.UpdateElementObjectModel" 
    xmlns:wssc1="http://schemas.datacontract.org/2004/07/WSSC.V4.DMS.EKV.WssDocsService.ObjectModel">
           <soapenv:Header/>
           <soapenv:Body>
              <tem:UpdateElement>
                 <tem:parameters>
                 
                    <wssc:ListID>{0}</wssc:ListID>
                    <wssc:UpdateItems>
                      
                       <wssc:UpdateItem>
                          <wssc:LookupItemId>{1}</wssc:LookupItemId>
                          <wssc:LookupValue>

                            {2}
                          
                          </wssc:LookupValue>
                       </wssc:UpdateItem>
                    
                    </wssc:UpdateItems>
                 </tem:parameters>
              </tem:UpdateElement>
           </soapenv:Body>
        </soapenv:Envelope>""".format(list_id, item_id, items_field)
    # print(body_request)

    # Try and check result of POST request
    is_correct = post(endpoint, body_request, 'UpdateElement')
    if is_correct:
        logger.info('Result: +')
        return True
    else:
        logger.info('Result: -')
        return False

def accept_document_solution(endpoint:str,
                            reg_number:str,
                            solution:str,
                            user_email:str,
                            comment: Optional[str],
                            email_to_send: Optional[str]):
    """
    Main function for create element
    :param endpoint: Url for wsdl
    :param list_id: ListID for add
    :param value: dict of FieldName:Value
    :return: (bool) True or False
    """

    if comment is not None:
        xml_comment = f'<wssc:CommentToSolution>{comment}</wssc:CommentToSolution>'
    else:
        xml_comment = ''

    if email_to_send is not None:
        xml_email = f'<wssc:Emails>{email_to_send}</wssc:Emails>'
    else:
        xml_email = ''

    xml_document_fields = """<wssc:DocumentFields>
                <!--Zero or more repetitions:-->
                <wssc:BaseDocumentField>
                    <!--Optional:-->
                    <wssc:Name>?</wssc:Name>
                </wssc:BaseDocumentField>
                </wssc:DocumentFields>"""
    xml_document_fields = '' # Plug

    # Generate body for WSDL
    body_request = f"""
    <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" 
    xmlns:tem="http://tempuri.org/" 
    xmlns:wssc="http://schemas.datacontract.org/2004/07/WSSC.V4.DMS.EKV.WssDocsService">
    <soapenv:Header/>
    <soapenv:Body>
        <tem:AcceptDocumentSolution>
            <tem:parameters>
                <!--Optional comment:-->
                {xml_comment}
                <!--Optional comment:-->
                
                {xml_email}
                <!--Core fields:-->
                <wssc:RegNumber>{reg_number}</wssc:RegNumber>
                <wssc:SolutionName>{solution}</wssc:SolutionName>
                <wssc:User>{user_email}</wssc:User>
            </tem:parameters>
        </tem:AcceptDocumentSolution>
    </soapenv:Body>
    </soapenv:Envelope>"""

    # Try and check result of POST request
    is_correct = post(endpoint, body_request, 'AcceptDocumentSolution')
    if is_correct:
        logger.debug('Result: +')
        return True
    else:
        logger.debug('Result: -')
        logger.debug(reg_number)
        logger.debug(body_request)
        return False



def update_some_elements(endpoint, list_id, items_update):
    """
    Main function for update element
    :param endpoint: (str) Url for wsdl
    :param list_id: (int) ListID for add
    :param item_id: (int) ItemID for add
    :param value: (dict) of FieldName:Value
    :return: (bool) True or False
    """


    # Generate body for WSDL
    body_request = """
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:tem="http://tempuri.org/" xmlns:wssc="http://schemas.datacontract.org/2004/07/WSSC.V4.DMS.EKV.WssDocsService.UpdateElementObjectModel" xmlns:wssc1="http://schemas.datacontract.org/2004/07/WSSC.V4.DMS.EKV.WssDocsService.ObjectModel">
           <soapenv:Header/>
           <soapenv:Body>
              <tem:UpdateElement>
                 <tem:parameters>

                    <wssc:ListID>{0}</wssc:ListID>
                    <wssc:UpdateItems>

                      {1} 

                    </wssc:UpdateItems>
                 </tem:parameters>
              </tem:UpdateElement>
           </soapenv:Body>
        </soapenv:Envelope>""".format(list_id, items_update)
    # print(body_request)

    # Try and check result of POST request
    is_correct = post(endpoint, body_request, 'UpdateElement')
    if is_correct:
        logger.info('Result: +')
        return True
    else:
        logger.info('Result: -')
        return False


def send_testing_post():
    import xml_soap
    #body = xml_soap.xml_body
    body = None
    endpoint = 'https://wssdocs.vostok-electra.ru/ekv/WssDocsService.svc'
    post(endpoint, body, 'CreateDocument')


if __name__ == '__main__':
    # post() # Just test post request: Search user
    send_testing_post()

    # create_element(config['web_service']['wsdl_docs'],
    #                                 869,
    #                                 {'ИНН': '123', 'КПП': '123', 'Договор АИС': '123'}
    #                                 )

    # update_element(config['web_service']['wsdl_test'],
    #                1626,
    #                606334,
    #                {'ИНН': '012', 'КПП': '012', 'Договор АИС': '123'}
    #                )

    # update_element(config['update_setting']['wsdl'],
    #                config['update_setting']['list_id'],
    #                226,
    #                {'КПП': '012'}
    #                )

    # accept_document_solution(config['web_service']['wsdl_docs'],
    #                         'ИТ-тест-2021-0085',
    #                         'Разослать',
    #                         'test2@wss-consulting.ru',
    #                         'тест1',
    #                         'test5@wss-consulting.ru')
