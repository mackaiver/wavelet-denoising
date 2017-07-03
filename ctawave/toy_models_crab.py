
import numpy as np
import astropy.units as u
import spectrum
import performance
from scipy import integrate, signal
from tqdm import tqdm
from IPython import embed


def simulate_steady_source_with_transient(
            x_pos_steady_source,
            y_pos_steady_source,
            x_pos_transient,
            y_pos_transient,
            df_A_eff,
            df_bg_rate,
            df_Ang_Res,
            num_slices=100,
            time_per_slice=30 * u.s,
            bins=[80, 80],
            E_min=0.1 * u.TeV,
            E_max=100 * u.TeV,
            fov_min=0 * u.deg,
            fov_max=12 * u.deg,
            ):

    cta_radius = 800 * u.m
    sim_area = 2*np.pi*(2*cta_radius)**2

    N_steady_source = spectrum.number_particles_crab(time_per_slice, E_min, E_max, sim_area)
    N_background_cta = int(df_bg_rate.bg_rate.sum() / (u.s) * time_per_slice)
    sample_factor_a_eff = performance.calc_a_eff_factor(df_A_eff, sim_area)

    ### ctools ###
    # N_steady_source = 621
    # N_background_cta = 11498
    # sample_factor_a_eff = 0.355877616747182

    # N_transient_max = 2*N_steady_source                                         # Random number for transient sample!!!
    # transient_scale = (N_transient_max*signal.gaussian(num_slices, std=5)).astype(int)  # arbitrary value for std!!

    pks_data = np.loadtxt('/home/lena/Dokumente/CTA/transient_data_2.txt')
    flare_interp = np.interp(range(140), pks_data[:, 0] - pks_data[:, 0].min(),  pks_data[:, 1])
    transient_scale = int(flare_interp/0.25*N_steady_source)
    slices = []
    for i in tqdm(range(num_slices)):
        folded_events_crab = performance.response(time_per_slice, N_steady_source, E_min, E_max, df_A_eff, sample_factor_a_eff, sim_area)
        ang_res_steady_source = performance.interp_ang_res(folded_events_crab, df_Ang_Res)
        RA_crab, DEC_crab = performance.sample_positions_steady_source(x_pos_steady_source, y_pos_steady_source, ang_res_steady_source)
        RA_bg, DEC_bg = performance.sample_positions_background_random(fov_min, fov_max, int(N_background_cta))
        if transient_scale[i] > 0:
            folded_events_transient = performance.response(time_per_slice, transient_scale[i], E_min, E_max, df_A_eff, sample_factor_a_eff, sim_area)
            ang_res_transinet = performance.interp_ang_res(folded_events_transient, df_Ang_Res)
            RA_tr, DEC_tr = performance.sample_positions_steady_source(x_pos_transient, y_pos_transient, ang_res_transinet)
        else:
            RA_tr, DEC_tr = [], []
        RA = np.concatenate([RA_bg, RA_tr, RA_crab])
        DEC = np.concatenate([DEC_bg, DEC_tr, DEC_crab])

        slices.append(np.histogram2d(RA, DEC, range=[[fov_min / u.deg, fov_max / u.deg], [fov_min / u.deg, fov_max / u.deg]], bins=bins)[0])

    return np.array(slices)


def simulate_steady_source(
            x_pos,
            y_pos,
            df_A_eff,
            df_bg_rate,
            df_Ang_Res,
            num_slices=100,
            time_per_slice=30 * u.s,
            bins=[80, 80],
            E_min=0.1 * u.TeV,
            E_max=100 * u.TeV,
            fov_min=0 * u.deg,
            fov_max=12 * u.deg,
        ):
    cta_radius = 800 * u.m
    sim_area = 2*np.pi*(2*cta_radius)**2

    N_steady_source = spectrum.number_particles_crab(time_per_slice, E_min, E_max, sim_area)
    N_background_cta = int(df_bg_rate.bg_rate.sum() / (u.s) * time_per_slice)
    sample_factor_a_eff = performance.calc_a_eff_factor(df_A_eff, sim_area)


    ### ctools ###
    # N_steady_source = 621
    # N_background_cta = 11498
    # sample_factor_a_eff = 0.355877616747182

    print(N_background_cta, N_steady_source, sample_factor_a_eff, sample_factor_a_eff*N_steady_source)
    slices = []
    for i in tqdm(range(num_slices)):
        folded_events_crab = performance.response(time_per_slice, N_steady_source, E_min, E_max, df_A_eff, sample_factor_a_eff, sim_area)
        ang_res_steady_source = performance.interp_ang_res(folded_events_crab, df_Ang_Res)

        RA_crab, DEC_crab = performance.sample_positions_steady_source(x_pos, y_pos, ang_res_steady_source)
        RA_bg, DEC_bg = performance.sample_positions_background_random(fov_min, fov_max, int(N_background_cta))
        RA = np.concatenate([RA_bg, RA_crab])
        DEC = np.concatenate([DEC_bg, DEC_crab])

        slices.append(np.histogram2d(RA, DEC, range=[[fov_min / u.deg, fov_max / u.deg], [fov_min / u.deg, fov_max / u.deg]], bins=bins)[0])

    return np.array(slices)
