clear
close all
clc

% readjsonc
jsonc_param = XuReadJsonc('./mgfpj_mcgpu.jsonc');
ImageDimension = jsonc_param.ImageDimension;
ImageDimensionZ = jsonc_param.ImageDimensionZ;

PixelSize = jsonc_param.PixelSize;
VoxelHeight = jsonc_param.VoxelHeight;
% convert to vox
img_vol_water = XuReadRaw(fullfile(jsonc_param.InputDir,jsonc_param.InputFiles),[jsonc_param.ImageDimension jsonc_param.ImageDimension jsonc_param.ImageDimensionZ]);
img_vol_water = flip(img_vol_water,2);
% 
write_header('./sample2.txt',ImageDimension,ImageDimensionZ,PixelSize,VoxelHeight);
data = [2*ones(length(img_vol_water(:)),1), img_vol_water(:)];
data(data == 0) = 0.0001;
writematrix(data,'./sample2.txt','WriteMode','append','Delimiter',' ');

write_header('./air22.txt',ImageDimension,ImageDimensionZ,PixelSize,VoxelHeight);
data = [ones(length(img_vol_water(:)),1),0.0001 * ones(length(img_vol_water(:)),1)];
writematrix(data,'air22.txt','WriteMode','append','Delimiter',' ');

%默认根据探测器大小也可以手动设置
nu = jsonc_param.DetectorElementCountHorizontal; % number of pixels in the image: Nx（实际要生成的图片大小）
nv = jsonc_param.DetectorElementCountVertical; % Ny 
dfv = jsonc_param.DetectorOffsetVertical/10;
dfh = jsonc_param.DetectorOffsetHorizontal/10;
voel_num = jsonc_param.ImageDimension;% 对应jsonc文件中的ImageDimension
voel_hnum = jsonc_param.ImageDimensionZ;
voxel_size = jsonc_param.PixelSize/10; % cm，对应jsonc文件中的PixelSize
Voxel_height = jsonc_param.VoxelHeight/10;
sdd = jsonc_param.SourceDetectorDistance/10;% cm,对应jsonc文件中的SourceDetectorDistance
sod = jsonc_param.SourceIsocenterDistance/10;% 对应jsonc文件中的SourceIsocenterDistance
detec_elnum= [jsonc_param.DetectorElementCountHorizontal, jsonc_param.DetectorElementCountVertical];
du = (jsonc_param.DetectorElementWidth/10)*(detec_elnum(1)/nu); % cm,每个像素放大detec_elnum/nu
dv = (jsonc_param.DetectorElementHeight/10)*(detec_elnum(2)/nv); 
% z_center = jsonc_param.ImageCenterZ/10;

%                                                                                                                                                                                                            bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb  = jsonc_param.ImageCenterZ/10; % 实际射线源偏移(cm)
delta_z = 0;
delta_zdetector = abs(2*delta_z*(1+(sdd-sod)/sod));% 对应探测器的扩大(cm)
delta_nv = ceil(delta_zdetector/dv); % 对应探测器的扩大(像素数量)


% 读取in文件，in文件包含了程序所需的各种输入文件路径和输入参数
MCparam = struct();

% MCparam1 = load_MCGPU_param('./waterHead_120_1000.in');
MCparam.total_histories = nv*nu*1000;
MCparam.seed_input = 20220918;
MCparam.gpu_id = 3;
MCparam.num_threads_per_block = 512;
MCparam.histories_per_thread = 1000;
MCparam.file_name_espc = '../Spectrum_110KVp1.txt';
shift_vec = [voel_num*voxel_size*0.5,voel_num*voxel_size*0.5,voel_hnum*Voxel_height*0.5-delta_z];
MCparam.source_pos = [sod,0,0] + shift_vec;
MCparam.source_dir = [-1 , 0 , 0];
MCparam.aperture = [-1 ;-1]; % cone beam
MCparam.output_proj_type = 1;
MCparam.file_name_output = jsonc_param.OutputDir;
MCparam.dummy_num_pixels = int32([nu+ceil(abs(dfh)/dv);nv+abs(delta_nv)+ceil(abs(dfv)/dv)]);
MCparam.total_num_pixels = MCparam.dummy_num_pixels(1)*MCparam.dummy_num_pixels(2);
MCparam.det_size = [nu*du+2*abs(dfh);nv*dv+delta_zdetector+2*abs(dfv)]; % 探测器的大小
MCparam.sdd = sdd;
MCparam.num_projections = jsonc_param.Views;
MCparam.D_angle = jsonc_param.TotalScanAngle/jsonc_param.Views; % ANGLE BETWEEN PROJECTIONS [degrees] (360\num_projections for full CT)
MCparam.angularROI = [0;3600];
MCparam.sod = sod;
MCparam.vertical_translation_per_projection = 0;
MCparam.flag_material_dose = 0;
MCparam.tally_3D_dose = 0;
MCparam.file_name_voxels = './sample2.txt'; %对应到转成的txt文件

MCparam.file_name_materials = {...
    '..\MCGPU-for-MATLAB-main\material\air__5-120keV.mcgpu.gz', ...
    '..\MCGPU-for-MATLAB-main\material\water__5-120keV.mcgpu.gz', ...
    '..\MCGPU-for-MATLAB-main\material\bone_ICRP110__5-120keV.mcgpu.gz', ...
    '..\MCGPU-for-MATLAB-main\material\adipose_ICRP110__5-120keV.mcgpu.gz', ...
    '..\MCGPU-for-MATLAB-main\material\brain_ICRP110__5-120keV.mcgpu.gz', ...
    '..\MCGPU-for-MATLAB-main\material\blood_ICRP110__5-120keV.mcgpu.gz', ...
    '..\MCGPU-for-MATLAB-main\material\breast_75-25_Hammerstein__5-120keV.mcgpu.gz', ...
    '..\MCGPU-for-MATLAB-main\material\cartilage_ICRP110__5-120keV.mcgpu.gz', ...
    '..\MCGPU-for-MATLAB-main\material\connective_Woodard__5-120keV.mcgpu.gz', ...
    '..\MCGPU-for-MATLAB-main\material\glands_others_ICRP110__5-120keV.mcgpu.gz', ...
    '..\MCGPU-for-MATLAB-main\material\liver_ICRP110__5-120keV.mcgpu.gz', ...
    '..\MCGPU-for-MATLAB-main\material\lung_ICRP110__5-120keV.mcgpu.gz', ...
    '..\MCGPU-for-MATLAB-main\material\muscle_ICRP110__5-120keV.mcgpu.gz', ...
    '..\MCGPU-for-MATLAB-main\material\PMMA__5-120keV.mcgpu.gz', ...
    '..\MCGPU-for-MATLAB-main\material\red_marrow_Woodard__5-120keV.mcgpu.gz', ...
    '..\MCGPU-for-MATLAB-main\material\skin_ICRP110__5-120keV.mcgpu.gz', ...
    '..\MCGPU-for-MATLAB-main\material\soft_tissue_ICRP110__5-120keV.mcgpu.gz', ...
    '..\MCGPU-for-MATLAB-main\material\stomach_intestines_ICRP110__5-120keV.mcgpu.gz', ...
    '..\MCGPU-for-MATLAB-main\material\titanium__5-120keV.mcgpu.gz',...
    ''};
% MCparam.file_name_materials = MCparam1.file_name_materials;
try
    MCparam.spec = parse_spectrum_file('../Spectrum_110KVp1.txt'); %目前这个需要自己添加  从jsonc文件里读入的话还未修改
    fprintf('spec file is successfully loaded!');
catch
    error('Spec file not found, please reload');
end

MCparam.spec.espc = MCparam.spec.espc/1000;
% MCparam.total_histories = nu*(nv+delta_nv)*5*10000;% 模拟的x射线总光子数


disp(MCparam)
MCGPU_mex('init', MCparam);

voxel_data = parse_vox_file('./sample2.txt');

[prime,compton,rayleign,Mscatter]=MCGPU_mex('run',voxel_data);
scatter_obj = compton+rayleign+Mscatter;
prime_obj = prime;
total = scatter_obj+prime_obj;
MCGPU_mex('clear');

figure;
for idx = 1:MCparam.num_projections
    imshow(prime_obj(:,delta_nv+1:end,idx),[]);
end

filename = 'bone';
for idx = 1:MCparam.num_projections
    filePath = sprintf('./sgm11/%s_%d.raw', filename, idx);
    proj = [prime(:,delta_nv+1:end,idx),scatter_obj(:,delta_nv+1:end,idx)]; %[primary, scatter]
%     disp(size(proj))
    XuWriteRaw(filePath,proj,'float32');
end

MCparam.num_projections = 40;
MCGPU_mex('init', MCparam);

voxel_data = parse_vox_file('./air22.txt');

[prime,compton,rayleign,Mscatter]=MCGPU_mex('run',voxel_data);
scatter_obj = compton+rayleign+Mscatter;
prime_obj = prime;
total = scatter_obj+prime_obj;
MCGPU_mex('clear');

figure;
for idx = 1:40
    imshow(prime_obj(:,delta_nv+1:end,idx),[]);
end

filename = 'air';
for idx = 1:MCparam.num_projections
    filePath = sprintf('./sgm12/%s_%d.raw', filename, idx);
    proj = [prime(:,delta_nv+1:end,idx),scatter_obj(:,delta_nv+1:end,idx)]; %[primary, scatter]
%     disp(size(proj))
    XuWriteRaw(filePath,proj,'float32');
end



function status = write_header(s_str,ImageDimension,ImageDimensionZ,PixelSize,VoxelHeight)
fid = fopen(s_str,'w');
fprintf(fid,'[SECTION VOXELS HEADER v.2008-04-13]\r\n');
fprintf(fid,[num2str(ImageDimension) ' ' num2str(ImageDimension) ' ' num2str(ImageDimensionZ) ' No. OF VOXELS IN X,Y,Z\r\n']);
fprintf(fid,[num2str(PixelSize/10) ' ' num2str(PixelSize/10) ' ' num2str(VoxelHeight/10) ' VOXEL SIZE (cm) ALONG X,Y,Z\r\n']);
fprintf(fid,' 1                  COLUMN NUMBER WHERE MATERIAL ID IS LOCATED\r\n');
fprintf(fid,' 2                  COLUMN NUMBER WHERE THE MASS DENSITY IS LOCATED\r\n');
fprintf(fid,' 0                  BLANK LINES AT END OF X,Y-CYCLES (1=YES,0=NO)\r\n');
fprintf(fid,' [END OF VXH SECTION]\r\n');
fclose(fid);
status = 1;
end


