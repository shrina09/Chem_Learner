import molecule

# radius = { 'H': 25,
# 'C': 40,
# 'O': 40,
# 'N': 40,
# }
# element_name = { 'H': 'grey',
# 'C': 'black',
# 'O': 'red',
# 'N': 'blue',
# }
header = """<svg version="1.1" width="1000" height="1000"
xmlns="http://www.w3.org/2000/svg">"""

footer = """</svg>"""
offsetx = 500
offsety = 500


class Atom:
    def __init__(self, c_atom):
        self.atom = c_atom
        self.z = c_atom.z


    def svg(self):
        #computes according the assignment description
        cx = (self.atom.x * 100.0) + offsetx
        cy = (self.atom.y * 100.0) + offsety
        atom_radius = radius[self.atom.element]
        atom_colour = element_name[self.atom.element]

        return '  <circle cx="%.2f" cy="%.2f" r="%d" fill="url(#%s)"/>\n' % (cx, cy, atom_radius, atom_colour)
    

    def __str__ (self):
        return f'element: {self.atom.element}, x: {self.atom.x}, y: {self.atom.y}, z: {self.atom.z}'


class Bond:
    def __init__(self, c_bond):
      self.bond = c_bond
      self.z = c_bond.z

    
    #TA Rithik and Zyan helped with this function
    def svg(self):
        c1x = self.bond.x1 * 100 + offsetx - (self.bond.dy * 10.0)
        c2x = self.bond.x1 * 100 + offsetx + (self.bond.dy * 10.0)
        c3x = self.bond.x2 * 100 + offsetx + (self.bond.dy * 10.0)
        c4x = self.bond.x2 * 100 + offsetx - (self.bond.dy * 10.0)

        c1y = self.bond.y1 * 100 + offsety + (self.bond.dx * 10.0)
        c2y = self.bond.y1 * 100 + offsety - (self.bond.dx * 10.0)
        c3y = self.bond.y2 * 100 + offsety - (self.bond.dx * 10.0)
        c4y = self.bond.y2 * 100 + offsety + (self.bond.dx * 10.0)
        
        return '  <polygon points="%.2f,%.2f %.2f,%.2f %.2f,%.2f %.2f,%.2f" fill="green"/>\n' % (
        c1x, c1y, c2x, c2y, c3x, c3y, c4x, c4y)
            
           
    def __str__ (self):
        return f"a1: {self.bond.a1}, a2: {self.bond.a2}, epairs: {self.bond.epairs}, x1: {self.bond.x1}, y1: {self.bond.y1}, x2: {self.bond.x2}, y2: {self.bond.y2}, z: {self.bond.z}, len: {self.bond.len}, dx: {self.bond.dx}, dy: {self.bond.dy} "


class Molecule(molecule.molecule):
    #TA Zyan helped with the function
    def svg (self):
        item_atoms = []
        item_bonds = []

        str_svg = ""
        for i in range(self.atom_no):
            item_atoms.append(self.get_atom(i))

        for i in range(self.bond_no):
            item_bonds.append(self.get_bond(i))

        i = 0
        j = 0
        k = 0

        arr = []

        while i < self.atom_no and j < self.bond_no:
            if  item_atoms[i].z < item_bonds[j].z:
                arr.append(Atom(item_atoms[i]))
                i += 1
            else:
                arr.append(Bond(item_bonds[j]))
                j += 1
            k += 1
  
        while i < self.atom_no:
            arr.append(Atom(item_atoms[i]))
            i += 1
            k += 1
  
        while j < self.bond_no:
            arr.append(Bond(item_bonds[j]))
            j += 1
            k += 1
        
        for m in arr:
            str_svg += m.svg()
        
        return f'{header}{str_svg}{footer}'
        
    
    #TA Niloy helped with this
    def parse(self, file_obj):
        #skips the first 3 lines 
        for i in range(3):
            file_content = next(file_obj)
        
        #getting the number of atom and bonds in the file
        file_content = next(file_obj)

        count_arr = file_content.split()
        atom_len = int(count_arr[0])
        bond_len = int(count_arr[1])
        
        #reading the atoms and appending the necessary data (according the instructions)
        file_atom = ""

        for i in range(atom_len):
            file_atom = next(file_obj)
            atom_arr = file_atom.split()

            x = float(atom_arr[0])
            y = float(atom_arr[1])
            z = float(atom_arr[2])
            element = (atom_arr[3])

            self.append_atom(element,x,y,z)

        #reading the bonds and appending the necessary data (according the instructions)
        file_bond = ""

        for i in range(bond_len):
            file_bond = next(file_obj)
            bond_arr = file_bond.split()

            a1_index = int(bond_arr[0]) - 1
            a2_index = int(bond_arr[1]) - 1
            epairs_val = int(bond_arr[2])

            self.append_bond(a1_index, a2_index, epairs_val)

    
    #TA Zyan helped with this function
    def __str__ (self):
        temp_str = ""

        for i in range(self.atom_no):
            temp_str += Atom(self.get_atom(i)).__str__()

        for i in range(self.bond_no):
            temp_str += Bond(self.get_bond(i)).__str__()

        return temp_str

