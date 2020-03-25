import create_cr_image_basic_text_sr_and_gsps
import create_ct_image
import create_enhanced_sr_tid_1500
import create_enhanced_sr_tid_1500_linear_measurements
import create_gsps_and_kos
import create_gsps_from_seg
import create_wsm_image

if __name__ == "__main__":
    create_cr_image_basic_text_sr_and_gsps.run()
    create_ct_image.run()
    create_enhanced_sr_tid_1500.run()
    create_enhanced_sr_tid_1500_linear_measurements.run()
    create_gsps_and_kos.run()
    create_gsps_from_seg.run()
    create_wsm_image.run()