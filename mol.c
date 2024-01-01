#include <stdio.h>
#include "mol.h"

//Setter for atom
void atomset( atom *atom, char element[3], double *x, double *y, double *z ) {
    atom->x = *x;
    atom->y = *y;
    atom->z = *z;
    strcpy(atom->element, element);
}

//Getter for atom 
void atomget( atom *atom, char element[3], double *x, double *y, double *z ) {
    *x = atom->x;
    *y = atom->y;
    *z = atom->z;
    strcpy(element, atom->element);
}

//Setter for bond
void bondset(bond *bond, unsigned short *a1, unsigned short *a2, atom **atoms, unsigned char *epairs ) {
    bond->a1 = *a1;
    bond->a2 = *a2;
    bond->epairs = *epairs;
    bond->atoms = *atoms;

    compute_coords(bond);
}

//Getter for bond
void bondget(bond *bond, unsigned short *a1, unsigned short *a2, atom **atoms, unsigned char *epairs) {
    *a1 = bond->a1;
    *a2 = bond->a2;
    *atoms = bond->atoms; 
    *epairs = bond->epairs;
}

void compute_coords( bond *bond ) {
    //Setting the xs and ys 
    bond->x1 = bond->atoms[bond->a1].x;
    bond->x2 = bond->atoms[bond->a2].x;

    bond->y1 = bond->atoms[bond->a1].y;
    bond->y2 = bond->atoms[bond->a2].y;
    
    //Calculating the z
    bond->z = ((bond->atoms[bond->a1].z)+ (bond->atoms[bond->a2].z)) / 2;
    
    //Calculating the len
    bond->len = sqrt(((bond->x2 - bond->x1) * (bond->x2 - bond->x1)) + ((bond->y2 - bond->y1) * (bond->y2 - bond->y1)));
   
    //Calculating dx and dy
    bond->dy = (bond->y2 - bond->y1) / bond->len;
    bond->dx = (bond->x2 - bond->x1) / bond->len;
}

molecule *molmalloc( unsigned short atom_max, unsigned short bond_max ) {
    //TA Tony helped me with the basics of this function
    
    //Intializing and allocating memory
    molecule *temp_mol = (molecule*)malloc(sizeof(molecule));

    temp_mol->atom_max = atom_max;
    temp_mol->bond_max = bond_max;

    temp_mol->atom_no = 0;
    temp_mol->bond_no = 0;
    
    //Allocating atoms with appropriate memory 
    temp_mol->atoms = (struct atom*)malloc(sizeof(struct atom)*atom_max);
    
    //If memory does not allocate properly (memory does not malloced properly)
    if (temp_mol->atoms == NULL) {
        free(temp_mol);
        fprintf(stderr, "Did not malloc properly, exiting the program\n");
        return NULL;
    }
    
    //Allocating atom_ptrs with appropriate memory 
    temp_mol->atom_ptrs = (struct atom**)malloc(sizeof(struct atom*)*atom_max);
    
    //If memory does not allocate properly (memory does not malloced properly)
    if (temp_mol->atom_ptrs == NULL) {
        free(temp_mol->atoms);
        free(temp_mol);
        fprintf(stderr, "Did not malloc properly, exiting the program\n");
        return NULL;
    }
    
    //Allocating bonds with appropriate memory 
    temp_mol->bonds = (struct bond*)malloc(sizeof(struct bond)*bond_max);

    //If memory does not allocate properly (memory does not malloced properly)
    if (temp_mol->bonds == NULL) {
        free(temp_mol->atom_ptrs);
        free(temp_mol->atoms);
        free(temp_mol);
        fprintf(stderr, "Did not malloc properly, exiting the program\n");
        return NULL;
    }
    
    //Allocating bond_ptrs with appropriate memory 
    temp_mol->bond_ptrs = (struct bond**)malloc(sizeof(struct bond*)*bond_max);

    //If memory does not allocate properly (memory does not malloced properly)
    if (temp_mol->bond_ptrs == NULL) {
        free(temp_mol->atom_ptrs);
        free(temp_mol->atoms);
        free(temp_mol->bonds);
        free(temp_mol);
        fprintf(stderr, "Did not malloc properly, exiting the program\n");
        return NULL;
    }

    return temp_mol;
}

molecule *molcopy( molecule *src ) {
    //creating the the molecule that will be a copy
    molecule *return_mol = molmalloc(src->atom_max, src->bond_max);
   
    //If memory does not allocate properly (memory does not malloced properly)
    if (return_mol == NULL) {
        fprintf(stderr, "Not mallocing properly\n");
        return NULL;
    }
    
    //Copying atoms and atom_ptrs
    for (int i = 0; i < src->atom_no; i++) {
        molappend_atom(return_mol, &(src->atoms[i]));
    }
    
    //Copying bonds and bond_ptrs
    for (int i = 0; i < src->bond_no; i++) {
        molappend_bond(return_mol, &(src->bonds[i]));
    }

    return return_mol;
}

//For freeing memory
void molfree( molecule *ptr ) {
    free(ptr->atoms);
    free(ptr->atom_ptrs);

    free(ptr->bonds);
    free(ptr->bond_ptrs);

    free(ptr);
}

//TA Tony and Rithik helped me with basics of this function 
void molappend_atom( molecule *molecule, atom *atom ) {
    if (molecule->atom_no == molecule->atom_max) {
        if (molecule->atom_max == 0) {
            molecule->atom_max = 1;
        } else {
            molecule->atom_max *= 2;
        }

        molecule->atoms = (struct atom*)realloc(molecule->atoms, sizeof(struct atom)*molecule->atom_max);

        //If memory does not realloc properly (realloc does not work properly)
        if (molecule->atoms == NULL) {
            free(molecule);
            fprintf(stderr, "realloc failed\n");
            exit(0);
        }
        
        molecule->atom_ptrs = (struct atom**)realloc(molecule->atom_ptrs, sizeof(struct atom*)*molecule->atom_max);

        //If memory does not realloc properly (realloc does not work properly)
        if (molecule->atom_ptrs == NULL) {
            free(molecule->atoms);
            free(molecule);
            fprintf(stderr, "realloc failed\n");
            exit(0);
        }
    }
    
    //Adding the atom at an empty index in atoms
    molecule->atoms[molecule->atom_no] = *atom;
   
    //Fixing atom_ptrs to accomadate the above change
    for(int i = 0; i <= molecule->atom_no; i++) {
       molecule->atom_ptrs[i] = &molecule->atoms[i];
    }
    
    //Incrementing atom_no to accomadate the added atom
    (molecule->atom_no)++;
}

//TA Tony and Rithik helped me with basics of this function
void molappend_bond( molecule *molecule, bond *bond ) {
    if (molecule->bond_no == molecule->bond_max) {
        if (molecule->bond_max == 0) {
            molecule->bond_max = 1;
         
        } else {
            molecule->bond_max *= 2;
        }

        molecule->bonds = (struct bond*)realloc(molecule->bonds, sizeof(struct bond)*molecule->bond_max);
        
        //If memory does not realloc properly (realloc does not work properly)
        if (molecule->bonds == NULL) {
            fprintf(stderr, "realloc failed\n");
            exit(0);
        }
       
        molecule->bond_ptrs = (struct bond**)realloc(molecule->bond_ptrs, sizeof(struct bond*)*molecule->bond_max);

        //If memory does not realloc properly (realloc does not work properly)
        if (molecule->bond_ptrs == NULL) {
            free(molecule->bonds);
            free(molecule);
            fprintf(stderr, "realloc failed\n");
            exit(0);
        }
    }
    
    //Adding the bond at an empty index in bonds
    molecule->bonds[molecule->bond_no] = *bond;
    
    //Fixing bonds_ptrs to accomadate the above change
    for(int i = 0; i <= molecule->bond_no; i++) {
        molecule->bond_ptrs[i] = &molecule->bonds[i];
    }
    
    //Incrementing bond_no to accomadate the added bond
    molecule->bond_no++;
}


void molsort( molecule *molecule ) {
    qsort(molecule->atom_ptrs, molecule->atom_no, sizeof(atom*),atom_comp);
    qsort(molecule->bond_ptrs, molecule->bond_no, sizeof(bond*),bond_comp); 
}

//Comparision function for atoms
int atom_comp(const void *a, const void *b) {
    atom **a_ptr, **b_ptr;

    a_ptr = (atom **)a;
    b_ptr = (atom **)b;
    
    if (((*a_ptr)->z) < ((*b_ptr)->z)) {
        return -1;
    }
    else if (((*a_ptr)->z) > ((*b_ptr)->z)) {
        return 1;
    } 
    else if (((*a_ptr)->z) == ((*b_ptr)->z)) {
        return 0;
    }

    return 0;
}

//Comparision function for bonds
int bond_comp(const void *a, const void *b) {
    bond **a_ptr, **b_ptr;

    a_ptr = (bond **)a;
    b_ptr = (bond **)b;

    if (((*a_ptr)->z) < ((*b_ptr)->z)) {
        return -1;
    }
    else if (((*a_ptr)->z) > ((*b_ptr)->z)) {
        return 1;
    } 
    else if (((*a_ptr)->z) == ((*b_ptr)->z)) {
        return 0;
    }

    return 0;
}

//The rotation matrix logic from the sites below:
//http://www.c-jump.com/bcc/common/Talk3/Math/Matrices/Matrices.html
//https://en.wikipedia.org/wiki/Transformation_matrix#Rotation
void xrotation( xform_matrix xform_matrix, unsigned short deg ) {
    double rad = deg * M_PI / 180.0;

    xform_matrix[0][0] = 1;
    xform_matrix[0][1] = 0;
    xform_matrix[0][2] = 0;

    xform_matrix[1][0] = 0;
    xform_matrix[1][1] = cos(rad);
    xform_matrix[1][2] = -sin(rad);

    xform_matrix[2][0] = 0;
    xform_matrix[2][1] = sin(rad);
    xform_matrix[2][2] = cos(rad);
}

void yrotation( xform_matrix xform_matrix, unsigned short deg ) {
    double rad = deg * M_PI / 180.0;

    xform_matrix[0][0] = cos(rad);
    xform_matrix[0][1] = 0;
    xform_matrix[0][2] = sin(rad);

    xform_matrix[1][0] = 0;
    xform_matrix[1][1] = 1;
    xform_matrix[1][2] = 0;

    xform_matrix[2][0] = -sin(rad);
    xform_matrix[2][1] = 0;
    xform_matrix[2][2] = cos(rad);
}

void zrotation( xform_matrix xform_matrix, unsigned short deg ) {
    double rad = deg * M_PI / 180;

    xform_matrix[0][0] = cos(rad);
    xform_matrix[0][1] = -sin(rad);
    xform_matrix[0][2] = 0;

    xform_matrix[1][0] = sin(rad);
    xform_matrix[1][1] = cos(rad);
    xform_matrix[1][2] = 0;

    xform_matrix[2][0] = 0;
    xform_matrix[2][1] = 0;
    xform_matrix[2][2] = 1;
}

//The basic logic of computing matrix multiplication from the site below: 
//https://www.javatpoint.com/matrix-multiplication-in-c
void mol_xform( molecule *molecule, xform_matrix matrix ) {
    //Array that will be used to store x,y,and z values of atom
    double arr_atoms[3]; 
    //Array that will be used to store the result of the matrix multiplication
    double result[3];
    
    //Goes through the atoms array
    for (int i = 0; i < molecule->atom_no; i++) {
        //Intial values of x,y, and z
        arr_atoms [0] = molecule->atoms[i].x;
        arr_atoms [1] = molecule->atoms[i].y;
        arr_atoms [2] = molecule->atoms[i].z;
        
        //Performs the matrix multiplication
        for(int j = 0;j < 3; j++) {    
            for(int m = 0; m < 3; m++) {    
                result [j] = 0;    
                for(int k=0; k<3; k++) {    
                    result[j] += matrix[j][k]* arr_atoms[k];    
                }    
            }    
        } 
        
        //Putting the result of the matrix multiplication to the corresponding x, y, and z values of the atom
        molecule->atoms[i].x = result[0];
        molecule->atoms[i].y = result[1];
        molecule->atoms[i].z = result[2];

    }
    
    //Accomodates the change in the bond struct
    for(int i = 0; i < molecule->bond_no; i++) {
        compute_coords(&molecule->bonds[i]);
    }
}
