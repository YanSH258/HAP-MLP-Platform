import dpdata
from ase.io import write
data = dpdata.System("batch_init", fmt="deepmd/npy")
perturb_atoms = data.to_ase_structure()
write("perturb.exyz", perturb_atoms, format='extxyz')