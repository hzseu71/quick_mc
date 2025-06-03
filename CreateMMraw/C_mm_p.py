from create_2mm_iodine import c_iodine2
from create_5mm_iodine import c_iodine5
from create_1mm_fe import c_fe1
from create_1mm_ta import c_ta1
from create_1mm_pt import c_pt1
from create_50mm_ba import c_ba50
from create_40mm_bone import c_bone40
from creat_co2_2mm import c_co2_2
from create_co2_5mm import c_co2_5
from create_pmma import c_pmma

for pmma_thickness in range(30, 31, 10):

    c_iodine2(pmma_thickness)
    c_iodine5(pmma_thickness)
    c_fe1(pmma_thickness)
    c_ta1(pmma_thickness)
    c_pt1(pmma_thickness)
    c_ba50(pmma_thickness)
    c_bone40(pmma_thickness)
    c_co2_2(pmma_thickness)
    c_co2_5(pmma_thickness)

    c_pmma(pmma_thickness)




