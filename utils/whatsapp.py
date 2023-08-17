import re
import pandas as pd
from datetime import datetime


class preprocesamiento:
    '''
    Métodos útiles para preprocesar todos los mensajes de un chat de whatsapp
    '''
    def leer(self,path:str,encoding:str='utf8') -> str:
        '''
        Recibe la ruta donde esta el chat y lo codifica.
        '''
        with open(path, encoding=encoding) as file:
            chat = file.read()

        return chat    


    def limpiar(self,chat:str)->str:
        '''
        Limpia las conversaciones y las separa entre mensaje e info de remitente
        '''
        chat = chat.replace('\u202f', '')
        chat = re.split('(\d+/\d+/\d\d\d\d,\s\d+:\d+\w.\w.)\s-\s', chat)[1:]
        chat = [sentence.replace('\n', '') for sentence in chat]

        return chat

    def __separar_mensaje__(self,message:str)->tuple:
        '''
        Separa el mensaje entre remitente y cuerpo del mensaje
        '''
        sep_message = message.split(':', 1)
        if len(sep_message) == 2:
            sender, body = sep_message
        else:
            sender, body = 'Chat', message

        return sender, body


    def convertir_a_dataframe(self,chat:str)->pd.DataFrame:
        '''
        Convierte el chat en un dataframe de pandas
        '''
        it = iter(chat)
        paired_chat = [[x, next(it)] for x in it]

        df = pd.DataFrame(paired_chat, columns = ['fecha', 'mensaje'])
        
        df['fecha'] = df['fecha'].str.replace('.','').copy()
        df['fecha'] = df['fecha'].str.upper().copy()
        df['fecha'] = df['fecha'].apply(lambda x: datetime.strptime(x, '%d/%m/%Y, %I:%M%p'))
        
        df['remitente'], df['mensaje'] = zip(*df['mensaje'].apply(self.__separar_mensaje__))
        
        df['elimina_info'] = df['mensaje'].apply(lambda x: True if 'eliminaste' in x.lower() or 'eliminó' in x.lower() else False)
        df['envia_link'] = df['mensaje'].apply(lambda x: True if 'https://' in x.lower() or 'http://' in x.lower() else False)
        df['envia_multimedia'] = df['mensaje'].apply(lambda x: True if 'multimedia omitido' in x.lower() else False)

        return df