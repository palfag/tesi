import sys
import email
import base64
import re
from tika import parser
import os




# REGEX TO CHECK
visa_card_pattern = '^(.|\n)*([0-9]{4}( |-)*){3}[0-9]{4}(.|\n)*'
codice_fiscale_pattern = '(.|\n)*([A-z]){6}([0-9]){2}[A-z]([0-9]){2}[A-z][0-9]{3}[A-z](.|\n)*'



filename = sys.stdin.read()


filename2 = "email.eml"
fd = open(filename2, 'w')
fd.write(filename)
#print(fd)
fd.close()



is_sensitive_data_found = False


msg = email.message_from_file(open(filename2))


content_type = msg.get('content-type')
type = content_type.split(';')[0]

# 2. Controlliamo se contiene allegati
#if msg.is_multipart():
if(type == 'multipart/mixed'):
    print("la seguente email contiene un allegato ed è da controllare")
    attachments = msg.get_payload()

   # 3. Per ogni allegato controlliamo se contiene dati sensibili
    for attachment in attachments:

        if attachment.get_filename() is not None:
           

            # 4. estrazione dell'estensione
            filename = attachment.get_filename()
            extension = filename.split(".")[-1]


            if(extension == "txt"):

                payload = attachment.get_payload()

                #print(payload)
                decoded = base64.b64decode(payload)

                #print(decoded)
                decoded_utf = decoded.decode("utf-8")

                print(decoded_utf)
                result = re.match(visa_card_pattern, decoded_utf) or \
                         re.match(codice_fiscale_pattern, decoded_utf)
                

                if result:
                    print("trovato dato sensibile")
                    is_sensitive_data_found = True
                    break
                else:
                    print("nessun dato sensibile trovato")


            elif (extension == "doc" or
                  extension == "pdf" or
                  extension == "csv" or
                  extension == "ppt"):


                bytes = attachment.get_payload(decode=True)
                

                new_filename = 'file.' + extension
                f = open(new_filename, 'wb')
                f.write(bytes)
                f.close()


                # Estrazione del testo utilizzando la libreria tika
                text = parser.from_file(new_filename, 'http://localhost:9998/tika')
                parsed_text = text['content']

                print(parsed_text)

                result = bool(re.match(visa_card_pattern, parsed_text) or\
                              re.match(codice_fiscale_pattern, parsed_text))

                os.remove(new_filename)

                if result:
                    print("trovato dato sensibile")
                    is_sensitive_data_found = True
                    break
                else:
                    print("nessun dato sensibile trovato")
            
            # Rifiutiamo l'email se contiene allegati di altre estensioni non gestite
            else:  
                is_sensitive_data_found = True
                break


    if is_sensitive_data_found:
        # MESSAGE REJECTED
        sys.exit(1)
    else:
        sys.exit(0)
else:
    print("la mail non contiene allegati")
    sys.exit(0)
