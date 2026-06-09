from itertools import product

def print_table_commands(varnames, pitnames, depths, repetitions):
    print()
    for var in varnames:
        print(f"Average({repetitions}, {var}, IEEE4, False)")
        fieldnames = [f"{var}_{pit}_{depth}cm_Avg" for pit, depth in product(pitnames, depths)]
        print('FieldNames("' + ",".join(fieldnames) + '")')
    for var in varnames:
        print(f"Sample({repetitions}, {var}, FP2)")
        fieldnames = [f"{var}_{pit}_{depth}cm" for pit, depth in product(pitnames, depths)]
        print('FieldNames("' + ",".join(fieldnames) + '")')
    

# soil moisture
pitnames = "AB"
depths = [5, 10, 30]
varnames = [
    "vwc", 
    "soil_cond", 
    "soil_temp", 
    "soil_temp_F", 
    "uncorr_soil_cond", 
    "uncorr_r_eps", 
    "uncorr_i_eps", 
    "r_eps", 
    "i_eps"    
]
print_table_commands(varnames, pitnames, depths, "NUM_HYDRA")



# heat flux plates
pitnames = "ABC"
depths = [5]
varnames = ["G"]
print_table_commands(varnames, pitnames, depths, "NUM_HFP")

"""
Sample(NUM_HYDRA, vwc, FP2)
FieldNames("vwc_A_5cm,vwc_A_10cm,vwc_A_15cm,vwc_A_30cm,vwc_A_50cm,vwc_B_5cm,vwc_B_10cm,vwc_B_15cm,vwc_B_30cm,vwc_B_50cm,vwc_C_5cm,vwc_C_10cm,vwc_C_15cm,vwc_C_30cm,vwc_C_50cm")
Sample(NUM_HYDRA, soil_cond, FP2)
FieldNames("soil_cond_A_5cm,soil_cond_A_10cm,soil_cond_A_15cm,soil_cond_A_30cm,soil_cond_A_50cm,soil_cond_B_5cm,soil_cond_B_10cm,soil_cond_B_15cm,soil_cond_B_30cm,soil_cond_B_50cm,soil_cond_C_5cm,soil_cond_C_10cm,soil_cond_C_15cm,soil_cond_C_30cm,soil_cond_C_50cm")
Sample(NUM_HYDRA, soil_temp, FP2)
FieldNames("soil_temp_A_5cm,soil_temp_A_10cm,soil_temp_A_15cm,soil_temp_A_30cm,soil_temp_A_50cm,soil_temp_B_5cm,soil_temp_B_10cm,soil_temp_B_15cm,soil_temp_B_30cm,soil_temp_B_50cm,soil_temp_C_5cm,soil_temp_C_10cm,soil_temp_C_15cm,soil_temp_C_30cm,soil_temp_C_50cm")
Sample(NUM_HYDRA, soil_temp_F, FP2)
FieldNames("soil_temp_F_A_5cm,soil_temp_F_A_10cm,soil_temp_F_A_15cm,soil_temp_F_A_30cm,soil_temp_F_A_50cm,soil_temp_F_B_5cm,soil_temp_F_B_10cm,soil_temp_F_B_15cm,soil_temp_F_B_30cm,soil_temp_F_B_50cm,soil_temp_F_C_5cm,soil_temp_F_C_10cm,soil_temp_F_C_15cm,soil_temp_F_C_30cm,soil_temp_F_C_50cm")
Sample(NUM_HYDRA, uncorr_soil_cond, FP2)
FieldNames("uncorr_soil_cond_A_5cm,uncorr_soil_cond_A_10cm,uncorr_soil_cond_A_15cm,uncorr_soil_cond_A_30cm,uncorr_soil_cond_A_50cm,uncorr_soil_cond_B_5cm,uncorr_soil_cond_B_10cm,uncorr_soil_cond_B_15cm,uncorr_soil_cond_B_30cm,uncorr_soil_cond_B_50cm,uncorr_soil_cond_C_5cm,uncorr_soil_cond_C_10cm,uncorr_soil_cond_C_15cm,uncorr_soil_cond_C_30cm,uncorr_soil_cond_C_50cm")
Sample(NUM_HYDRA, uncorr_r_eps, FP2)
FieldNames("uncorr_r_eps_A_5cm,uncorr_r_eps_A_10cm,uncorr_r_eps_A_15cm,uncorr_r_eps_A_30cm,uncorr_r_eps_A_50cm,uncorr_r_eps_B_5cm,uncorr_r_eps_B_10cm,uncorr_r_eps_B_15cm,uncorr_r_eps_B_30cm,uncorr_r_eps_B_50cm,uncorr_r_eps_C_5cm,uncorr_r_eps_C_10cm,uncorr_r_eps_C_15cm,uncorr_r_eps_C_30cm,uncorr_r_eps_C_50cm")
Sample(NUM_HYDRA, uncorr_i_eps, FP2)
FieldNames("uncorr_i_eps_A_5cm,uncorr_i_eps_A_10cm,uncorr_i_eps_A_15cm,uncorr_i_eps_A_30cm,uncorr_i_eps_A_50cm,uncorr_i_eps_B_5cm,uncorr_i_eps_B_10cm,uncorr_i_eps_B_15cm,uncorr_i_eps_B_30cm,uncorr_i_eps_B_50cm,uncorr_i_eps_C_5cm,uncorr_i_eps_C_10cm,uncorr_i_eps_C_15cm,uncorr_i_eps_C_30cm,uncorr_i_eps_C_50cm")
Sample(NUM_HYDRA, r_eps, FP2)
FieldNames("r_eps_A_5cm,r_eps_A_10cm,r_eps_A_15cm,r_eps_A_30cm,r_eps_A_50cm,r_eps_B_5cm,r_eps_B_10cm,r_eps_B_15cm,r_eps_B_30cm,r_eps_B_50cm,r_eps_C_5cm,r_eps_C_10cm,r_eps_C_15cm,r_eps_C_30cm,r_eps_C_50cm")
Sample(NUM_HYDRA, i_eps, FP2)
FieldNames("i_eps_A_5cm,i_eps_A_10cm,i_eps_A_15cm,i_eps_A_30cm,i_eps_A_50cm,i_eps_B_5cm,i_eps_B_10cm,i_eps_B_15cm,i_eps_B_30cm,i_eps_B_50cm,i_eps_C_5cm,i_eps_C_10cm,i_eps_C_15cm,i_eps_C_30cm,i_eps_C_50cm")

Average(NUM_HYDRA, vwc, IEEE4, False)
FieldNames("vwc_A_5cm_Avg,vwc_A_10cm_Avg,vwc_A_15cm_Avg,vwc_A_30cm_Avg,vwc_A_50cm_Avg,vwc_B_5cm_Avg,vwc_B_10cm_Avg,vwc_B_15cm_Avg,vwc_B_30cm_Avg,vwc_B_50cm_Avg,vwc_C_5cm_Avg,vwc_C_10cm_Avg,vwc_C_15cm_Avg,vwc_C_30cm_Avg,vwc_C_50cm_Avg")
Average(NUM_HYDRA, soil_cond, IEEE4, False)
FieldNames("soil_cond_A_5cm_Avg,soil_cond_A_10cm_Avg,soil_cond_A_15cm_Avg,soil_cond_A_30cm_Avg,soil_cond_A_50cm_Avg,soil_cond_B_5cm_Avg,soil_cond_B_10cm_Avg,soil_cond_B_15cm_Avg,soil_cond_B_30cm_Avg,soil_cond_B_50cm_Avg,soil_cond_C_5cm_Avg,soil_cond_C_10cm_Avg,soil_cond_C_15cm_Avg,soil_cond_C_30cm_Avg,soil_cond_C_50cm_Avg")
Average(NUM_HYDRA, soil_temp, IEEE4, False)
FieldNames("soil_temp_A_5cm_Avg,soil_temp_A_10cm_Avg,soil_temp_A_15cm_Avg,soil_temp_A_30cm_Avg,soil_temp_A_50cm_Avg,soil_temp_B_5cm_Avg,soil_temp_B_10cm_Avg,soil_temp_B_15cm_Avg,soil_temp_B_30cm_Avg,soil_temp_B_50cm_Avg,soil_temp_C_5cm_Avg,soil_temp_C_10cm_Avg,soil_temp_C_15cm_Avg,soil_temp_C_30cm_Avg,soil_temp_C_50cm_Avg")
Average(NUM_HYDRA, soil_temp_F, IEEE4, False)
FieldNames("soil_temp_F_A_5cm_Avg,soil_temp_F_A_10cm_Avg,soil_temp_F_A_15cm_Avg,soil_temp_F_A_30cm_Avg,soil_temp_F_A_50cm_Avg,soil_temp_F_B_5cm_Avg,soil_temp_F_B_10cm_Avg,soil_temp_F_B_15cm_Avg,soil_temp_F_B_30cm_Avg,soil_temp_F_B_50cm_Avg,soil_temp_F_C_5cm_Avg,soil_temp_F_C_10cm_Avg,soil_temp_F_C_15cm_Avg,soil_temp_F_C_30cm_Avg,soil_temp_F_C_50cm_Avg")
Average(NUM_HYDRA, uncorr_soil_cond, IEEE4, False)
FieldNames("uncorr_soil_cond_A_5cm_Avg,uncorr_soil_cond_A_10cm_Avg,uncorr_soil_cond_A_15cm_Avg,uncorr_soil_cond_A_30cm_Avg,uncorr_soil_cond_A_50cm_Avg,uncorr_soil_cond_B_5cm_Avg,uncorr_soil_cond_B_10cm_Avg,uncorr_soil_cond_B_15cm_Avg,uncorr_soil_cond_B_30cm_Avg,uncorr_soil_cond_B_50cm_Avg,uncorr_soil_cond_C_5cm_Avg,uncorr_soil_cond_C_10cm_Avg,uncorr_soil_cond_C_15cm_Avg,uncorr_soil_cond_C_30cm_Avg,uncorr_soil_cond_C_50cm_Avg")
Average(NUM_HYDRA, uncorr_r_eps, IEEE4, False)
FieldNames("uncorr_r_eps_A_5cm_Avg,uncorr_r_eps_A_10cm_Avg,uncorr_r_eps_A_15cm_Avg,uncorr_r_eps_A_30cm_Avg,uncorr_r_eps_A_50cm_Avg,uncorr_r_eps_B_5cm_Avg,uncorr_r_eps_B_10cm_Avg,uncorr_r_eps_B_15cm_Avg,uncorr_r_eps_B_30cm_Avg,uncorr_r_eps_B_50cm_Avg,uncorr_r_eps_C_5cm_Avg,uncorr_r_eps_C_10cm_Avg,uncorr_r_eps_C_15cm_Avg,uncorr_r_eps_C_30cm_Avg,uncorr_r_eps_C_50cm_Avg")
Average(NUM_HYDRA, uncorr_i_eps, IEEE4, False)
FieldNames("uncorr_i_eps_A_5cm_Avg,uncorr_i_eps_A_10cm_Avg,uncorr_i_eps_A_15cm_Avg,uncorr_i_eps_A_30cm_Avg,uncorr_i_eps_A_50cm_Avg,uncorr_i_eps_B_5cm_Avg,uncorr_i_eps_B_10cm_Avg,uncorr_i_eps_B_15cm_Avg,uncorr_i_eps_B_30cm_Avg,uncorr_i_eps_B_50cm_Avg,uncorr_i_eps_C_5cm_Avg,uncorr_i_eps_C_10cm_Avg,uncorr_i_eps_C_15cm_Avg,uncorr_i_eps_C_30cm_Avg,uncorr_i_eps_C_50cm_Avg")
Average(NUM_HYDRA, r_eps, IEEE4, False)
FieldNames("r_eps_A_5cm_Avg,r_eps_A_10cm_Avg,r_eps_A_15cm_Avg,r_eps_A_30cm_Avg,r_eps_A_50cm_Avg,r_eps_B_5cm_Avg,r_eps_B_10cm_Avg,r_eps_B_15cm_Avg,r_eps_B_30cm_Avg,r_eps_B_50cm_Avg,r_eps_C_5cm_Avg,r_eps_C_10cm_Avg,r_eps_C_15cm_Avg,r_eps_C_30cm_Avg,r_eps_C_50cm_Avg")
Average(NUM_HYDRA, i_eps, IEEE4, False)
FieldNames("i_eps_A_5cm_Avg,i_eps_A_10cm_Avg,i_eps_A_15cm_Avg,i_eps_A_30cm_Avg,i_eps_A_50cm_Avg,i_eps_B_5cm_Avg,i_eps_B_10cm_Avg,i_eps_B_15cm_Avg,i_eps_B_30cm_Avg,i_eps_B_50cm_Avg,i_eps_C_5cm_Avg,i_eps_C_10cm_Avg,i_eps_C_15cm_Avg,i_eps_C_30cm_Avg,i_eps_C_50cm_Avg")

Sample(NUM_HYDRA, G, FP2)
FieldNames("G_A_5cm,G_B_5cm,G_C_5cm")

Average(NUM_HYDRA, G, IEEE4, False)
FieldNames("G_A_5cm_Avg,G_B_5cm_Avg,G_C_5cm_Avg")


"""
