import os
import yaml
import numpy as np
import SimpleITK as sitk
from pydicom.dataset import Dataset
import glob
from pydicom.dataset import FileMetaDataset
import pydicom
import sys
import argparse

class Nii2Dcm:
    def __init__(self, nii_file_path, config_file_path, output_directory):
        self.nii_file_path = nii_file_path
        self.nii_filename = os.path.splitext(os.path.basename(nii_file_path))[0]
        self.config_file_path = config_file_path
        self.output_directory = output_directory

        self.load_files()
        self.get_image_properties()
        self.process_nii_data()

    def load_files(self):
        self.nii_img = sitk.ReadImage(self.nii_file_path)
        with open(self.config_file_path, 'r') as file:
            self.config = yaml.safe_load(file)

    def get_image_properties(self):
        self.nii_transform = self.nii_img.GetDirection()
        self.original_spacing = self.nii_img.GetSpacing()
        self.original_origin = self.nii_img.GetOrigin()
        print(f'direction:{self.nii_transform} \noriginal_spacing: {self.original_spacing} \noriginal_origin:{self.original_origin}')

    def process_nii_data(self, bias=2240):
        self.nii_data = sitk.GetArrayFromImage(self.nii_img)
        self.nii_data = self.nii_data.astype(np.uint16)
        self.window_center = np.mean(self.nii_data)
        self.window_width = (np.percentile(self.nii_data,95) - np.percentile(self.nii_data,5)) * 2
        print(f'window_center:{self.window_center} window_width:{self.window_width}')


    def create_save_dicom_slices(self):
        image_count = self.nii_data.shape[0]
        for i in range(image_count):
            img_slice = self.nii_data[i, :, :]
            dcm_img = self.create_dicom_slice(img_slice, i)
            self.save_dicom_slice(dcm_img, i)
        print(f'Converting {self.nii_filename}.nii complete.\n')


    def create_dicom_slice(self, img_slice, i):
        dcm_img = Dataset()
        dcm_img = self.update_dicom_attributes(dcm_img, img_slice, i)
        return dcm_img

    def update_dicom_attributes(self, dcm_img, img_slice, i):
        # Basic attributes
        dcm_img.Rows, dcm_img.Columns = img_slice.shape
        dcm_img.BitsAllocated = 16
        dcm_img.BitsStored = 16
        dcm_img.HighBit = 15
        dcm_img.PixelRepresentation = 0
        dcm_img.SamplesPerPixel = 1
        dcm_img.PixelData = img_slice.flatten().tobytes()

        # NIfTI-related attributes
        dcm_img.ImageOrientationPatient = [tr for tr in self.nii_transform][:6]
        dcm_img.PatientID = self.nii_filename
        dcm_img.StudyInstanceUID = self.nii_filename
        dcm_img.SeriesInstanceUID = self.nii_filename + ".0"
        dcm_img.SOPInstanceUID = dcm_img.SeriesInstanceUID +'.'+ str(i)
        dcm_img.PixelSpacing = [self.original_spacing[0], self.original_spacing[1]]
        dcm_img.SliceThickness = self.original_spacing[2]
        dcm_img.InstanceNumber = str(i + 1)
        dcm_img.ImagePositionPatient = [self.original_origin[0], self.original_origin[1], self.original_origin[2] + i*self.original_spacing[2]]
        dcm_img.SliceLocation = self.original_origin[2] + i*self.original_spacing[2]
        dcm_img.WindowCenter = self.window_center
        dcm_img.WindowWidth = self.window_width
        
        # Config-related attributes
        for tag, value in self.config.items():
            setattr(dcm_img, tag, value)

        dcm_img.file_meta = FileMetaDataset()
        dcm_img.file_meta.TransferSyntaxUID = pydicom.uid.ImplicitVRLittleEndian
        dcm_img.file_meta.MediaStorageSOPClassUID =  dcm_img.SOPClassUID # CT Image Storage```python
        dcm_img.file_meta.MediaStorageSOPInstanceUID = dcm_img.SOPInstanceUID

        return dcm_img

    def save_dicom_slice(self, dcm_img, i):
        file_name = str(i+1).zfill(5)  # Pad the file number with leading zeroes
        output_path = os.path.join(self.output_directory, self.nii_filename)
        os.makedirs(output_path, exist_ok=True)
        save_path = os.path.join(output_path, f'{file_name}.dcm')
        dcm_img.save_as(save_path)
        print(f'saved {save_path}.dcm')

def process_directory(input_directory, output_directory):
    nii_files = glob.glob(os.path.join(input_directory, '*.nii'))
    for nii_file_path in nii_files:
        print(f'Converting {nii_file_path}')
        nii2dcm = Nii2Dcm(nii_file_path, 'config.yaml', output_directory)
        nii2dcm.create_save_dicom_slices()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Convert NIfTI files to DICOM.')
    parser.add_argument('--input', default='input', help='Input directory containing .nii files.')
    parser.add_argument('--output', default='output', help='Output directory for .dcm files.')
    args = parser.parse_args() 
    process_directory(args.input, args.output)
    print("Press any key to exit...")
    sys.stdin.read(1)
    
