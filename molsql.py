import os
import sqlite3
import MolDisplay

class Database: 
    def __init__(self, reset=False):
        #creates the data base according to the conditions in the assignment description
        if reset == True:
            if os.path.isfile('molecules.db'):
                os.remove('molecules.db')
        
        self.conn = sqlite3.connect( 'molecules.db' ) 

    
    def create_tables(self):       
        #creates Elements table if it does not exist
        self.conn.execute( """CREATE TABLE IF NOT EXISTS Elements (
                        ELEMENT_NO INTEGER NOT NULL,
                        ELEMENT_CODE VARCHAR(3) PRIMARY KEY NOT NULL,
                        ELEMENT_NAME VARCHAR(32) NOT NULL,
                        COLOUR1 CHAR(6) NOT NULL,
                        COLOUR2 CHAR(6) NOT NULL,
                        COLOUR3 CHAR(6) NOT NULL, 
                        RADIUS DECIMAL(3) NOT NULL);""" )
        
        #creates Atoms table if it does not exist
        self.conn.execute( """CREATE TABLE IF NOT EXISTS Atoms (
                        ATOM_ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                        ELEMENT_CODE VARCHAR(3) NOT NULL,
                        X DECIMAL(7,4) NOT NULL,
                        Y DECIMAL(7,4) NOT NULL,
                        Z DECIMAL(7,4) NOT NULL,
                        FOREIGN KEY (ELEMENT_CODE) REFERENCES Elements(ELEMENT_CODE)
                    );""" )
        
        #creates Bonds table if it does not exist
        self.conn.execute( """CREATE TABLE IF NOT EXISTS Bonds (
                        BOND_ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                        A1 INTEGER NOT NULL,
                        A2 INTEGER NOT NULL,
                        EPAIRS INTEGER NOT NULL);""" )
        
        #creates Molecule table if it does not exist
        self.conn.execute( """CREATE TABLE IF NOT EXISTS Molecules (
                        MOLECULE_ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                        NAME TEXT UNIQUE NOT NULL);""" )
        
        #creates MoleculeAtom table if it does not exist
        self.conn.execute( """CREATE TABLE IF NOT EXISTS MoleculeAtom (
                        MOLECULE_ID INTEGER NOT NULL REFERENCES Molecules(MOLECULE_ID),
                        ATOM_ID INTEGER NOT NULL REFERENCES Atoms(ATOM_ID), PRIMARY KEY(MOLECULE_ID,ATOM_ID));""" )
        
        #creates MoleculeBond table if it does not exist
        self.conn.execute( """CREATE TABLE IF NOT EXISTS MoleculeBond (
                        MOLECULE_ID INTEGER NOT NULL REFERENCES Molecules(MOLECULE_ID),
                        BOND_ID INTEGER NOT NULL REFERENCES Bonds(BOND_ID), PRIMARY KEY(MOLECULE_ID,BOND_ID));""" )
    
   
    def __setitem__( self, table, values):
        #creating the string that will hold the values
        val_arr = "(" + ",".join(["?"]* len(values)) + ")"
        
        #creating the string to that inserts the values in the table (commands)
        insert_arr = f"INSERT INTO {table} VALUES {val_arr}"
        
        #inserting the insert_arr and the values in the table
        self.conn.execute(insert_arr, values)
        self.conn.commit()


   #TA Niloy helped with this function
    def add_atom( self, molname, atom):
        #building the tuple
        atom_vals = (atom.atom.element, atom.atom.x, atom.atom.y, atom.atom.z)

        #insert the tuple in the table
        insert_atoms = "INSERT INTO ATOMS (ELEMENT_CODE, X, Y, Z) VALUES (?, ?, ?, ?)"
        self.conn.execute(insert_atoms, atom_vals)
        self.conn.commit()

        #get the last added row from Atoms table
        last_row = "SELECT * FROM ATOMS WHERE ATOM_ID = (SELECT MAX(ATOM_ID) FROM ATOMS)"
        row_cursor = self.conn.execute(last_row)
        atom_id = row_cursor.fetchone()[0]

        #find the molecule with name molname from the MoleculesTable
        molecule_with_molname = f"SELECT * FROM Molecules WHERE NAME=(?)"
        molecule_cursor = self.conn.execute(molecule_with_molname, (molname,))
        molecule_id = molecule_cursor.fetchone()[0]

        #insert the molecule id and atom id
        insert_to_mol_atom = "INSERT INTO MOLECULEATOM (MOLECULE_ID, ATOM_ID) VALUES (?, ?)"
        self.conn.execute(insert_to_mol_atom, (molecule_id, atom_id))
        self.conn.commit()
    
   
    #TA Niloy and Zyan helped with this function
    def add_bond(self, molname, bond ):
        #building the tuple
        bond_vals = (bond.bond.a1, bond.bond.a2, bond.bond.epairs)

        cursor = self.conn.cursor()
        
        #insert the tuple in the table
        insert_bonds = "INSERT INTO Bonds (A1, A2, EPAIRS) VALUES (?,?,?)"
        cursor.execute(insert_bonds, bond_vals)

        #getting the bond id
        bond_id = cursor.lastrowid

        #find the molecule with name molname from the MoleculesTable
        molecule_with_molname = f"SELECT * FROM Molecules WHERE NAME=(?)"
        molecule_cursor = self.conn.execute(molecule_with_molname, (molname,))
        molecule_id = molecule_cursor.fetchone()[0]

        #insert the molecule id and bond id
        insert_to_mol_atom = "INSERT INTO MOLECULEBOND (MOLECULE_ID, BOND_ID) VALUES (?, ?)"
        self.conn.execute(insert_to_mol_atom, (molecule_id, bond_id))
        self.conn.commit()
   
    
    #TA Niloy helped with this function
    def add_molecule( self, name, fp ):
        mol = MolDisplay.Molecule()

        mol.parse(fp)

        #add molecule to the molecule table
        add_mol = "INSERT INTO MOLECULES (NAME) VALUES (?)"
        self.conn.execute(add_mol, (name,))
        self.conn.commit()

        #using add_atom and add_bond according to assignment instructions
        for i in range(mol.atom_no):
            self.add_atom(name, MolDisplay.Atom(mol.get_atom(i)))

        for i in range(mol.bond_no):
            self.add_bond(name,MolDisplay.Bond(mol.get_bond(i)))
    
    # def delete_E(self, E_code):
    #     cursor = self.conn.cursor()

    #     cursor.execute("""DELETE FROM Elements
    #                         WHERE ELEMENT_CODE = ?""", (E_code,))
    #     self.conn.commit()


    #TA Niloy helped with this function
    def load_mol( self, name ):
        mol = MolDisplay.Molecule()
        
        #joining the Atom and MoleculeAtom table together
        join_atom = """
                        SELECT *
                        FROM Atoms
                        JOIN MoleculeAtom ON Atoms.ATOM_ID = MoleculeAtom.ATOM_ID
                        JOIN Molecules ON MoleculeAtom.MOLECULE_ID = Molecules.MOLECULE_ID
                        WHERE Molecules.NAME = ?  ORDER BY ATOM_ID ASC;
                    """
        
        #getting the table info
        atom_tup = self.conn.execute(join_atom, (name,)).fetchall()
        
        #joining the Bond and MoleculeBond table together
        join_bond = """
                        SELECT *
                        FROM Bonds
                        JOIN MoleculeBond ON Bonds.BOND_ID = MoleculeBond.BOND_ID
                        JOIN Molecules ON MoleculeBond.MOLECULE_ID = Molecules.MOLECULE_ID
                        WHERE Molecules.NAME = ?  ORDER BY BOND_ID ASC;
                    """
        
        #getting the table info
        bond_tup = self.conn.execute(join_bond, (name,)).fetchall()
        
        #appending the bond and atom information in bond and atom using append_atom and append_bond (according to assignment description)
        for i in range(len(atom_tup)):
            mol.append_atom(atom_tup[i][1], atom_tup[i][2], atom_tup[i][3], atom_tup[i][4])
        
        for i in range(len(bond_tup)):
            mol.append_bond(bond_tup[i][1], bond_tup[i][2], bond_tup[i][3])
        
        return mol
    
    
    def radius( self ):
        #getting the ELEMENT_CODE and RADIUS from Elements table
        rad_cursor = self.conn.execute("SELECT ELEMENT_CODE, RADIUS FROM Elements")
        rad_info = rad_cursor.fetchall()
         
        #creating and returning a dictionary with the ELEMENT_CODE as the key to the coressponding RADIUS values
        rad_dict = {}

        for info in rad_info:
            rad_dict[info[0]] = info[1]

        return rad_dict
    

    def element_name( self ):
        #getting the ELEMENT_CODE and ELEMENT_NAME from Elements table
        name_cursor = self.conn.execute("SELECT ELEMENT_CODE, ELEMENT_NAME FROM Elements")
        name_info = name_cursor.fetchall()
        
        #creating and returning a dictionary with the ELEMENT_CODE as the key to the coressponding ELEMENT_NAME values
        name_dict = {}

        for info in name_info:
            name_dict[info[0]] = info[1]
            
        return name_dict
    

    def radial_gradients( self ):
        #creating a string that will be concatenated later and returned (according to assignment description)
        return_str = ""
        
        #getting the necessary data out of the elements table
        grad_cursor = self.conn.execute("SELECT ELEMENT_NAME, COLOUR1, COLOUR2, COLOUR3 FROM Elements")
        grad_info = grad_cursor.fetchall()
       
        #adding the data to the string provided in the assignment description and concatenating it as the data is added (according to assignment description) and returning the concatenated string
        for content in grad_info:
            radial_gradient_SVG = """
<radialGradient id="%s" cx="-50%%" cy="-50%%" r="220%%" fx="20%%" fy="20%%">
  <stop offset="0%%" stop-color="#%s"/>
  <stop offset="50%%" stop-color="#%s"/>
  <stop offset="100%%" stop-color="#%s"/>
</radialGradient>""" % (content[0], content[1], content[2], content[3])
            
            return_str += radial_gradient_SVG
        
        return return_str
    

    #For default values
    def add_molecule( self, name, fp ):
        mol = MolDisplay.Molecule()

        #parsing the file
        mol.parse(fp)

        #For inserting the name in the molecule table 
        mol_insert = "INSERT INTO Molecules (NAME) VALUES (?)"
        self.conn.execute(mol_insert, (name,))
        self.conn.commit()

        #For adding default elements in the table that are not in the elements table but are in the sdf file
        for i in range(mol.atom_no):
            #Getting the current atom and then the required data from it to populate the elements table with that element/atom and inserting that into the elements table
            curr_atom = MolDisplay.Atom(mol.get_atom(i))
            
            elm_code = curr_atom.atom.element

            mol_insert = f"INSERT INTO Elements (ELEMENT_NO, ELEMENT_CODE, ELEMENT_NAME, COLOUR1, COLOUR2, COLOUR3, RADIUS) \
                    SELECT 1, '{elm_code}', '{elm_code}', 'FFF2CC', 'DF7857', 'E21818', 40 \
                    WHERE NOT EXISTS (SELECT 1 FROM Elements WHERE ELEMENT_CODE = '{elm_code}')"

            self.conn.execute(mol_insert)
            self.add_atom(name, curr_atom)

        #For adding all the bonds from the sdf file to the database
        for j in range(mol.bond_no):
            self.add_bond(name, MolDisplay.Bond(mol.get_bond(j)))
   
    
    def get_mol_info(self):
        cursor = self.conn.cursor()

        #Getting the molecule data
        mol_select = """SELECT Molecules.MOLECULE_ID, Molecules.NAME, COUNT(DISTINCT Bonds.BOND_ID), COUNT(DISTINCT Atoms.ATOM_ID)
                    FROM Molecules
                    JOIN MoleculeBond ON Molecules.MOLECULE_ID = MoleculeBond.MOLECULE_ID
                    JOIN Bonds ON MoleculeBond.BOND_ID = Bonds.BOND_ID
                    JOIN MoleculeAtom ON Molecules.MOLECULE_ID = MoleculeAtom.MOLECULE_ID
                    JOIN Atoms ON MoleculeAtom.ATOM_ID = Atoms.ATOM_ID
                    GROUP BY Molecules.MOLECULE_ID"""
        
        cursor.execute(mol_select)

        mol_selected = cursor.fetchall()
        
        #For getting all the molecules from the table and putting it into an array and returning the array of molecules
        mol_data = [] 

        for mol_select in mol_selected:
            mol_name = mol_select[1]
            num_bonds = mol_select[2]
            num_atoms = mol_select[3]

            mol = {
                "name": mol_name,
                "bond_count": num_bonds,
                "atom_count": num_atoms
            }

            mol_data.append(mol)

        return mol_data
        

    #Checking if the element exits or not in the table 
    def mol_fill(self, name):
        #For going through molecules table using its name
        cursor = self.conn.cursor()

        mol_select = "SELECT * FROM Molecules WHERE NAME = ?"

        cursor.execute(mol_select, (name,))
        
        #If it is exits return true if not then return false
        mol_there = cursor.fetchone()

        if mol_there is None:
            return False
        else:
            return True
        
        