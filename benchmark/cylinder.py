#!/usr/bin/env python
# coding: utf-8

import datetime
from itertools import count, product

import numpy as np
import pandas as pd

from capytaine.reference_bodies import HorizontalCylinder
from capytaine.symmetries import *

from benchmark import *

WORKING_DIRECTORY = datetime.datetime.now().strftime("%Y-%m-%d_%H%M%S")

ID = count()

def full_resolution_Nemoh(nb_slices, nb_theta, omega_range):
    cylinder = HorizontalCylinder(length=10.0, radius=1.0, nx=nb_slices+1, nr=0, ntheta=nb_theta+1)
    cylinder.translate_x(-5.0)
    cylinder.translate_z(-2.0)
    return profile_Nemoh(cylinder, omega_range, f"{WORKING_DIRECTORY}/{next(ID)}_Nemoh_{nb_theta*nb_slices}")

def full_Capytaine(nb_slices, nb_theta, omega_range):
    cylinder = HorizontalCylinder(length=10.0, radius=1.0, nx=nb_slices+1, nr=0, ntheta=nb_theta+1)
    cylinder.translate_x(-5.0)
    cylinder.translate_z(-2.0)
    cylinder.dofs["Heave"] = cylinder.faces_normals @ (0, 0, 1)
    return profile_capytaine(cylinder, omega_range, f"{WORKING_DIRECTORY}/{next(ID)}_capy_{nb_theta*nb_slices}")

def sym_Capytaine(nb_slices, nb_theta, omega_range):
    cylinder = HorizontalCylinder(length=10.0, radius=1.0, nx=nb_slices+1, nr=0, ntheta=nb_theta+1)
    cylinder.translate_x(-5.0)
    cylinder.translate_z(-2.0)
    half_cylinder = cylinder.extract_faces(np.where(cylinder.faces_centers[:, 1] > 0)[0])
    half_cylinder.name = "half_cylinder"
    sym_cylinder = ReflectionSymmetry(half_cylinder, xOz_Plane)
    sym_cylinder.dofs["Heave"] = sym_cylinder.faces_normals @ (0, 0, 1)
    return profile_capytaine(sym_cylinder, omega_range, f"{WORKING_DIRECTORY}/{next(ID)}_sym_capy_{nb_theta*nb_slices}")

def sym_sym_Capytaine(nb_slices, nb_theta, omega_range):
    cylinder = HorizontalCylinder(length=10.0, radius=1.0, nx=nb_slices+1, nr=0, ntheta=nb_theta+1)
    cylinder.translate_x(-5.0)
    cylinder.translate_z(-2.0)
    half_cylinder = cylinder.extract_faces(np.where(cylinder.faces_centers[:, 1] > 0)[0])
    quarter_cylinder = half_cylinder.extract_faces(np.where(half_cylinder.faces_centers[:, 0] > 0)[0])
    quarter_cylinder.name = "quarter_cylinder"
    sym_sym_cylinder = ReflectionSymmetry(ReflectionSymmetry(quarter_cylinder, xOz_Plane), yOz_Plane)
    sym_sym_cylinder.dofs["Heave"] = sym_sym_cylinder.faces_normals @ (0, 0, 1)
    return profile_capytaine(sym_sym_cylinder, omega_range, f"{WORKING_DIRECTORY}/{next(ID)}_sym_sym_capy_{nb_theta*nb_slices}")

def trans_Capytaine(nb_slices, nb_theta, omega_range):
    ring = HorizontalCylinder(length=10.0/nb_slices, radius=1.0, nx=2, nr=0, ntheta=nb_theta+1)
    ring.translate_x(-5.0)
    ring.translate_z(-2.0)
    ring.name = "ring"
    trans_cylinder = TranslationalSymmetry(ring, translation=np.asarray([10.0/nb_slices, 0.0, 0.0]), nb_repetitions=nb_slices-1)
    trans_cylinder.dofs["Heave"] = trans_cylinder.faces_normals @ (0, 0, 1)
    return profile_capytaine(trans_cylinder, omega_range, f"{WORKING_DIRECTORY}/{next(ID)}_trans_capy_{nb_theta*nb_slices}")

def trans_sym_Capytaine(nb_slices, nb_theta, omega_range):
    ring = HorizontalCylinder(length=10.0/nb_slices, radius=1.0, nx=2, nr=0, ntheta=nb_theta+1)
    half_ring = ring.extract_faces(np.where(ring.faces_centers[:, 1] > 0)[0])
    half_ring.translate_x(-5.0)
    half_ring.translate_z(-2.0)
    half_ring.name = "half_ring"
    trans_cylinder = ReflectionSymmetry(TranslationalSymmetry(half_ring, translation=np.asarray([10.0/nb_slices, 0.0, 0.0]), nb_repetitions=nb_slices-1), xOz_Plane)
    trans_cylinder.dofs["Heave"] = trans_cylinder.faces_normals @ (0, 0, 1)
    return profile_capytaine(trans_cylinder, omega_range, f"{WORKING_DIRECTORY}/{next(ID)}_trans_sym_capy_{nb_theta*nb_slices}")

def sym_trans_Capytaine(nb_slices, nb_theta, omega_range):
    ring = HorizontalCylinder(length=10.0/nb_slices, radius=1.0, nx=2, nr=0, ntheta=nb_theta+1)
    half_ring = ring.extract_faces(np.where(ring.faces_centers[:, 1] > 0)[0])
    half_ring.translate_x(-5.0)
    half_ring.translate_z(-2.0)
    half_ring.name = "half_ring"
    trans_cylinder = TranslationalSymmetry(ReflectionSymmetry(half_ring, xOz_Plane), translation=np.asarray([10.0/nb_slices, 0.0, 0.0]), nb_repetitions=nb_slices-1)
    trans_cylinder.dofs["Heave"] = trans_cylinder.faces_normals @ (0, 0, 1)
    return profile_capytaine(trans_cylinder, omega_range, f"{WORKING_DIRECTORY}/{next(ID)}_sym_trans_capy_{nb_theta*nb_slices}")

# ===============================================================
# ===============================================================
# ===============================================================

nb_repetitions = 1
nb_theta = 30
nb_slices_range = range(10, 70, 10)
omega_range = [1.0] # np.linspace(0.1, 4.0, 10)

cases = {
    # "Nemoh 2.0":                           full_resolution_Nemoh,
    "Capytaine":                          full_Capytaine,
    "Capytaine + symmetry":               sym_Capytaine,
    # "Capytaine + 2 symmetries":           sym_sym_Capytaine,
    "Capytaine + translation":            trans_Capytaine,
    "Capytaine + translation + symmetry": trans_sym_Capytaine,
    "Capytaine + symmetry + translation": sym_trans_Capytaine,
    }

# ===========================

times = pd.DataFrame(
    index=range(nb_repetitions*len(nb_slices_range)),
    columns=["nb_cells"] + list(cases.keys()),
)

for i, (nb_slices, k) in enumerate(product(nb_slices_range, range(nb_repetitions))):
    print(f"====> Slices: {nb_slices}, Repetition: {k+1}/{nb_repetitions}")
    times["nb_cells"][i] = nb_slices*nb_theta
    for name, function in cases.items():
        print("\t\t" + name)
        times[name][i] = function(nb_slices, nb_theta, omega_range)

print(times)
times.to_csv(f'{WORKING_DIRECTORY}/times.csv')