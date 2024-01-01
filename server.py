import MolDisplay
import json
import cgi
import molsql
import sys
import io
import urllib
from http.server import HTTPServer, BaseHTTPRequestHandler
import molecule


db = molsql.Database(reset=True)
db.create_tables()


public_files = [ '/index.html', '/addRemove.html','/upload.html','/molSelect.html','/displayRot.html','/style.css', '/script.js' ]


class MyHandler(BaseHTTPRequestHandler):
    ang = [0,0,0]

    curr_mol = "Empty"

    def do_GET(self):
        if self.path in public_files:
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            fp = open( self.path[1:] )
            page = fp.read()
            fp.close()
            
            self.send_header("Content-length", len(page))
            self.end_headers()

            self.wfile.write(bytes(page, "utf-8"))
        elif (self.path == '/returnMol'):
            #Getting the molecule data
            mol = db.get_mol_info()

            #If there is no data in the database send a 204
            if len(mol) == 0:
                self.send_response(204)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                return
            
            #If everything is ok
            self.send_response(200) 
            self.send_header("Content-type", "application/json")
            self.end_headers()
            molecules_json = json.dumps(mol)
            self.wfile.write(bytes(molecules_json, "utf-8"))
        elif (self.path == '/recvSvg'):
            #If there is no molecule in the database send a 204
            if (MyHandler.curr_mol == "Empty"):
                self.send_response(204)
                self.send_header("Content-type", "image/svg+xml")
                self.end_headers()
                return
            
            #If everything is ok 
            self.send_response( 200 )
            self.send_header("Content-type", "image/svg+xml") 
            self.end_headers()

            #Getting the required data from the database and adding it to the appropriate places in MolDisplay so the svg can be generated
            MolDisplay.radius = db.radius()
            MolDisplay.element_name = db.element_name()
            MolDisplay.header += db.radial_gradients()

            mol = db.load_mol(MyHandler.curr_mol)

            #For the rotations (using mol.c)
            if (MyHandler.ang[0] != 0):
                mx = molecule.mx_wrapper(int(MyHandler.ang[0]), 0, 0)
                mol.xform( mx.xform_matrix )
            if (MyHandler.ang[1] != 0):
                mx = molecule.mx_wrapper(0, int(MyHandler.ang[1]), 0)
                mol.xform( mx.xform_matrix )
            if (MyHandler.ang[2] != 0):
                mx = molecule.mx_wrapper(0, 0, int(MyHandler.ang[2]))
                mol.xform( mx.xform_matrix )
            mol.sort()

            self.wfile.write( bytes( mol.svg(), "utf-8" ) ) 
        else:
            #If the page is not found
            self.send_response(404)
            self.end_headers()
            self.wfile.write(bytes("404: not found", "utf-8"))


    def do_POST(self):
        #For adding the elements
        if self.path == '/elementadd':
            len_cont= int (self.headers['Content-length'])

            body_cont = self.rfile.read(len_cont)

            var_post = urllib.parse.parse_qs(body_cont.decode('utf-8'))
            
            #Getting the data user entered from the webpage
            E_num = var_post['Enum'][0]
            E_code = var_post['Ecode'][0]
            E_name = var_post['Ename'][0]
            E_col1 = var_post['Ecolour1'][0][1:]
            E_col2 = var_post['Ecolour2'][0][1:]
            E_col3 = var_post['Ecolour3'][0][1:]
            radius = var_post['radius'][0]
            
            #Adding it to the elements table
            db['Elements'] = (E_num, E_code, E_name, E_col1, E_col2, E_col3, radius)

            sucess_msg = "Entry to element is sucessful"
            
            #If everything is ok
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.send_header('Content-length', len(sucess_msg))
            self.end_headers()
        elif(self.path == "/elementDelete"):
            #Deleting the elements 
            cont_len = int(self.headers['Content-Length'])

            body = self.rfile.read(cont_len)

            vars_post = urllib.parse.parse_qs( body.decode( 'utf-8' ) )

            #Getting the name of the element the user entered to delete
            E_name = str(vars_post['Ename'][0])
            
            #For deleting the element from the element table
            cursor = db.conn.cursor()
            cursor.execute("""DELETE FROM Elements WHERE ELEMENT_NAME = ?""", (E_name,))
            db.conn.commit()

            msg = "Sucessful delete"

            #If everything goed ok
            self.send_response( 200 )
            self.send_header( "Content-type", "text/plain" )
            self.send_header( "Content-length", len(msg) )
            self.end_headers()
        elif self.path == '/SdfUpload':
            #For uploading the sdf files 
            #Getting the file name and the molecule name the user entered
            rec_form = cgi.FieldStorage(self.rfile, headers = self.headers, environ = {'REQUEST_METHOD': 'POST'})
           
            #Storing the name of the file and the name of the molecule in a variable
            m_name = rec_form['Mname'].value
            file_sdf = rec_form['file_sdf'].value

            #Making sure the file has the sdf extension if not printing out a message on the console
            disp_cont = rec_form['file_sdf'].headers['Content-Disposition']

            filename = cgi.parse_header(disp_cont)[1]['filename']

            check_sdf =  filename.split('.')[-1]

            if (check_sdf != 'sdf'):
                print("Invalid file extension")

            #For making the molecule
            file_byte = io.BytesIO(file_sdf)
            
            file = io.TextIOWrapper(file_byte)

            #For adding the molecule in the database
            db.add_molecule(m_name, file)

            #If everything is ok
            resp_body = "Done"

            resp_len = len(resp_body.encode('utf-8'))

            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.send_header("Content-length", resp_len)
            self.end_headers()

            self.wfile.write(resp_body.encode('utf-8'))
        elif self.path == "/molShow":
            #For showing the molecule
            len_cont = int(self.headers['Content-Length'])

            body = self.rfile.read(len_cont)

            #For getting the molecule name and saving it
            vars_post = urllib.parse.parse_qs( body.decode( 'utf-8' ) )

            name_mol = str(vars_post['molName'][0])

            MyHandler.curr_mol = name_mol
            
            #Generating svg
            mol = MolDisplay.Molecule()

            mol = db.load_mol(name_mol)

            mol.sort()

            MolDisplay.radius = db.radius()

            MolDisplay.element_name = db.element_name()

            MolDisplay.header += db.radial_gradients()

            svg = mol.svg()

            #If everything is ok
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.send_header("Content-length", len(svg))
            self.end_headers()

            self.wfile.write(svg.encode('utf-8'))
        elif (self.path == "/rotView"):
            #For viewing the rotations
            len_cont = int(self.headers['Content-Length'])

            body = self.rfile.read(len_cont)

            #Getting the rotation (what type)
            vars_post = urllib.parse.parse_qs(body.decode('utf-8'))
            
            axis_rot = vars_post['axis'][0]

            #Performing the rotation depending on the type
            if (axis_rot == "x"):
                MyHandler.ang[0] = (MyHandler.ang[0] + 10) % 360
            elif (axis_rot == "y"):
                MyHandler.ang[1] = (MyHandler.ang[1] + 10) % 360
            elif (axis_rot == "z"):
                MyHandler.ang[2] = (MyHandler.ang[2] + 10) % 360
            
            body_res = "change sucessful"

            response_length = len(body_res.encode('utf-8'))

            #If everything is ok
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.send_header("Content-length", response_length)
            self.end_headers()

            self.wfile.write(body_res.encode('utf-8'))
        else:
            #If the page is not found
            self.send_error(404)
            self.end_headers()
            self.wfile.write(bytes("404: not found", "utf-8"))


httpd = HTTPServer(('localhost', int(sys.argv[1])), MyHandler)
httpd.serve_forever()

