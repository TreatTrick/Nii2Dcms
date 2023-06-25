# Nii2Dcms
a python script to convert .nii file to a series of .dcm files

## how to use it
First, you need to install the requirements.txt by running 
```
pip install -r requirements.txt
```
After that, you can run 
```
python Nii2Dcms.py
```
to convert the .nii files in the defualt `input` directory to .dcm files and save them into the default `output` directory.

Or you can run 
```
python Nii2Dcms.py --input=/your/input/directory --output=/your/output/directory
```
to convert the .nii files in the `/your/input/directory` to .dcm files and save them into the `/your/output/directory` directory.

## Important Notes
1. `config.yaml` contains the tag configuration of the generated DICOM files, which can be modified. For example, if you modify `PatientName: 'xyz'`, the patient name in the generated DICOM file will be `xyz`.
2. By default, all the .nii files under the `input` folder will be read and the generated DICOM files will be automatically saved to the directory corresponding to the .nii file name under the `output` folder.
For example, if there is a file `12345.nii` in the `input` folder, the directory 12345 will be generated in the `output` folder, and the .dcm files converted from `12345.nii` will be saved in the directory
