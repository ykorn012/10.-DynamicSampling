#======================================================================================================
# !/usr/bin/env python
# title          : LocalW2W_FWC_Run.py
# description    : Semiconductor Fab Wide Control using FDC, VM, R2R, L2L
# author         : Youngil Jung
# date           : 2019-06-17
# version        : v0.8
# usage          : python LocalW2W_FWC_Run.py
# notes          : Reference Paper "Virtual metrology and feedback control for semiconductor manufacturing"
# python_version : v3.5.3
#======================================================================================================
import numpy as np
from simulator.VM_Process1_시뮬레이터 import VM_Process1_시뮬레이터
from simulator.VM_Process1_DynamicSampling_노이즈시뮬레이터 import VM_Process1_DynamicSampling_노이즈시뮬레이터
from simulator.VM_Process2_시뮬레이터 import VM_Process2_시뮬레이터
from simulator.FDC_Graph import FDC_Graph
import os
# from pandas import DataFrame, Series
# import pandas as pd

os.chdir("D:/10. 대학원/04. Source/09. VM_Source/10. DynamicSampling/")

A_p1 = np.array([[0.5, -0.2], [0.25, 0.15]])    #recipe gain matrix
d_p1 = np.array([[0.1, 0], [0.05, 0]])  #drift matrix
C_p1 = np.transpose(np.array([[0, 0.5, 0.05, 0, 0.15, 0], [0.085, 0, 0.025, 0.2, 0, 0]])) # FDC variable matrix
# Process 변수와 출력 관련 system gain matrix

A_p2 = np.array([[1, 0.1], [-0.5, 0.2]])
d_p2 = np.array([[0, 0.05], [0, 0.05]])
C_p2 = np.transpose(np.array([[0.1, 0, 0, -0.2, 0.1], [0, -0.2, 0, 0.3, 0]]))
F_p2 = np.array([[2, 0], [0, 2]])
SEED1 = 111999999  #111999999
SEED2 = 1490  #1490 999999999
# Process 변수와 출력 관련 system gain matrix
M = 10
Z_DoE = 12
Z_VM = 50
Nz_RUN = 15

v1_PLS = 0.6
v2_PLS = 0.6

M = 10
S1 = 20
dM = 5
S2 = 60
RUNS_CNT = S1 + S2
N = M * S1 + dM * S2
dStart = S1 + 1  #25 * 10 + 30 * 5
Z_DoE = 12
v_PLS = 0.6
Nz_RUN = 15
old_N = 50 #40 60

def main():
    noise_ez_run = np.loadtxt('output/noise_ez_run.csv', delimiter=",", dtype=np.float32)
    abnormal_p2_ez_all_run_q2 = np.loadtxt('D:/10. 대학원/04. Source/09. VM_Source/04. VMOnly/output/abnormal_p2_ez_all_run_q2.csv', delimiter=",", dtype=np.float32)
    before_normal_p2_ez_all_run_q2 = np.loadtxt('D:/10. 대학원/04. Source/09. VM_Source/04. VMOnly/output/before_normal_p2_ez_all_run_q2.csv', delimiter=",", dtype=np.float32)
    fdh_graph = FDC_Graph()
    fwc_p1_vm = VM_Process1_시뮬레이터(A_p1, d_p1, C_p1, SEED1)
    fwc_p1_vm.DoE_Run(lamda_PLS=v1_PLS, Z=Z_DoE, M=M)  # DoE Run
    Normal_VMResult, Normal_ACTResult, ez_run, o_y_act, o_y_prd, _ = fwc_p1_vm.VM_Run(lamda_PLS=v1_PLS, Z=Z_VM, M=M)

    fwc_p1_vm = VM_Process1_DynamicSampling_노이즈시뮬레이터(A_p1, d_p1, C_p1, dM, dStart, SEED1)
    fwc_p1_vm.DoE_Run(lamda_PLS=v_PLS, Z=Z_DoE, M=M)  # DoE Run
    VM_Output, ACT_Output, ez_run, p1_y_act, p1_y_prd, p1_ez_all_run_q1 = fwc_p1_vm.VM_Run(lamda_PLS=v_PLS, Z=RUNS_CNT, M=M)

    #fdh_graph.plt_show1(N, p1_y_act[:, 0:1], p1_y_prd[:, 0:1])

    ez_run_out = []
    noise_ez_run_out = []
    runM = M
    noise_ez_run_out.append(np.array([0, 0]))
    for z in np.arange(1, old_N + 1):
        for k in np.arange(z * M, (z + 1) * M):
            noise_ez_run_out.append(noise_ez_run[z])
    noise_ez_run_out = np.array(noise_ez_run_out)

    ez_run_out.append(np.array([0, 0]))
    for z in np.arange(1, RUNS_CNT + 1):
        if z == dStart:
            runM = dM
        for k in np.arange(z * runM, (z + 1) * runM):
            ez_run_out.append(ez_run[z])
    ez_run_out = np.array(ez_run_out)

    #fdh_graph.plt_show5(ez_run_out, N, M, dM, S1, Noise=True)
    #fdh_graph.plt_show5_1(noise_ez_run_out, ez_run_out, N, M, dM, S1, type=1)

    p1_q1_mape_Queue = []

    # metrology 마다 보여주는 MAPE 값이 의미가 없다.
    for z in np.arange(Nz_RUN, Z_VM, 1):
        mape = fdh_graph.mean_absolute_percentage_error(z + 1, p1_y_act[((z + 1) * M) - 1][0], p1_y_prd[((z + 1) * M) - 1][0])
        p1_q1_mape_Queue.append(mape)

    print('Process-1 q1 Every Metrology MAPE After 15 Lot : {0:.2f}%'.format(np.mean(p1_q1_mape_Queue)))
    p1_q1_mape_Queue = []

    for i in np.arange(Nz_RUN * M, Z_VM * M, 1):
        mape = fdh_graph.mean_absolute_percentage_error(i + 1, p1_y_act[i][0], p1_y_prd[i][0])
        p1_q1_mape_Queue.append(mape)

    print('Process-1 q1 All MAPE After 15 Lot : {0:.2f}%'.format(np.mean(p1_q1_mape_Queue)))

    fwc_p2_act = VM_Process2_시뮬레이터(A_p2, d_p2, C_p2, F_p2, v1_PLS, p1_y_prd, p1_y_act, SEED2)
    fwc_p2_act.DoE_Run(lamda_PLS=v2_PLS, Z=Z_DoE, M=M, f=o_y_act)  # DoE Run ACT값으로 가능
    p2_VM_Output, p2_ACT_Output, p2_ez_run, p2_y_act, p2_y_prd, p2_ez_all_run_q2 = fwc_p2_act.VM_Run(lamda_PLS=v2_PLS, Z=Z_VM, M=M)

    #fdh_graph.plt_show1(Z_VM * M, p2_y_act[:, 1:2], p2_y_prd[:, 1:2])
    #fdh_graph.plt_show2(Z_VM, p2_ez_run[:, 0:1], p2_ez_run[:, 1:2], Noise=True)
    fdh_graph.plt_show1(Z_VM * M, p2_y_act[:, 1:2], p2_y_prd[:, 1:2], 'Process-2 Abnormal Case with Process-1 Dynamic Sampling', '2')
    fdh_graph.plt_show2_2(Z_VM * M, abnormal_p2_ez_all_run_q2[:, 1:2], p2_ez_all_run_q2[:, 1:2], 'Process-2 UPStream Rule X with Process-1 Dynamic Sampling', '2', color1='bx-', color2='rx--')

    #fdh_graph.plt_show2_2(Z_VM * M, abnormal_p2_ez_all_run_q2[:, 1:2], p2_ez_all_run_q2[:, 1:2], before_normal_p2_ez_all_run_q2[:, 1:2], 'Process-2 Abnormal Case', '2', color1='bx-', color2='rx--', color3='gx--')

    p2_q2_mape_Queue = []

    # metrology 마다 보여주는 MAPE 값이 의미가 없다.
    for z in np.arange(Nz_RUN, Z_VM, 1):
        mape = fdh_graph.mean_absolute_percentage_error(z + 1, p2_y_act[((z + 1) * M) - 1][1], p2_y_prd[((z + 1) * M) - 1][1])
        #print("으아아악 : ", p2_y_act[((z + 1) * M) - 1][1], p2_y_prd[((z + 1) * M) - 1][1])
        p2_q2_mape_Queue.append(mape)

    print('Process-2 q2 Every Metrology MAPE After 15 Lot : {0:.2f}%'.format(np.mean(p2_q2_mape_Queue)))
    p2_q2_mape_Queue = []

    for i in np.arange(Nz_RUN * M, Z_VM * M, 1):
        mape = fdh_graph.mean_absolute_percentage_error(i + 1, p2_y_act[i][1], p2_y_prd[i][1])
        p2_q2_mape_Queue.append(mape)

    print('Process-2 q2 All MAPE After 15 Lot : {0:.2f}%'.format(np.mean(p2_q2_mape_Queue)))


if __name__ == "__main__":
    main()
