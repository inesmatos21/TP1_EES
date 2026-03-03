#include "rapl.h"

int cpu_model;
int core = 0;

double package_before, package_after;
double pp0_before, pp0_after;
double pp1_before = 0.0, pp1_after;
double dram_before = 0.0, dram_after;

double power_units, energy_units, time_units;

int open_msr(int core) {
    char msr_filename[BUFSIZ];
    int fd;

    sprintf(msr_filename, "/dev/cpu/%d/msr", core);
    fd = open(msr_filename, O_RDONLY);
    if (fd < 0) {
        if (errno == ENXIO) {
            fprintf(stderr, "[WARNING] rdmsr: No CPU %d\n", core);
            exit(2);
        } else if (errno == EIO) {
            fprintf(stderr, "[WARNING] rdmsr: CPU %d doesn't support MSRs\n", core);
            exit(3);
        } else {
            perror("rdmsr:open");
            fprintf(stderr, "[ERROR] Trying to open %s\n", msr_filename);
            exit(127);
        }
    }

    return fd;
}

uint64_t read_msr(int fd, int which) {
  uint64_t data = (uint64_t)-1;

  if (pread(fd, &data, sizeof(data), (off_t)which) != sizeof(data)) {
    if (errno == EIO) {
        fprintf(stderr, "[WARNING] MSR 0x%x not available on this CPU.\n", which);
    } else {
        fprintf(stderr, "[ERROR] reading MSR 0x%x: %s\n", which, strerror(errno));
    }
    return (uint64_t)-1;
  }

  return data;
}


#include <stdio.h>
#include <string.h>


#define CPU_SANDYBRIDGE         42
#define CPU_SANDYBRIDGE_EP      45
#define CPU_IVYBRIDGE           58
#define CPU_IVYBRIDGE_EP        62
#define CPU_HASWELL             60
#define CPU_HASWELL_ULT         69
#define CPU_HASWELL_GT3E        70
#define CPU_HASWELL_EP          63
#define CPU_BROADWELL           61
#define CPU_BROADWELL_GT3E      71
#define CPU_BROADWELL_EP        79
#define CPU_BROADWELL_DE        86
#define CPU_SKYLAKE             78
#define CPU_SKYLAKE_HS          94
#define CPU_SKYLAKE_X           85
#define CPU_KNIGHTS_LANDING     87
#define CPU_KNIGHTS_MILL        133
#define CPU_KABYLAKE_MOBILE     142
#define CPU_KABYLAKE            158
#define CPU_ATOM_SILVERMONT     55
#define CPU_ATOM_AIRMONT        76
#define CPU_ATOM_MERRIFIELD     74
#define CPU_ATOM_MOOREFIELD     90
#define CPU_ATOM_GOLDMONT       92
#define CPU_ATOM_GEMINI_LAKE    122
#define CPU_ATOM_DENVERTON      95
#define CANNONLAKE_L            102
#define ICELAKE_L               126
#define ICELAKE                 125
#define COMETLAKE_L             166
#define COMETLAKE               165
#define TIGERLAKE_L             140
#define TIGERLAKE               141
#define ALDERLAKE               151
#define ALDERLAKE_L             154
#define ALDERLAKE_N             190
#define RAPTORLAKE              183
#define RAPTORLAKE_P            186
#define RAPTORLAKE_S            191
#define METEORLAKE              172
#define METEORLAKE_L            170
#define ICELAKE_D               108
#define ICELAKE_X               106
#define SAPPHIRERAPIDS_X        143
#define EMERALDRAPIDS_X         207

int detect_cpu(void) {
    FILE *fff;
    int family, model = -1;
    char buffer[BUFSIZ], *result;
    char vendor[BUFSIZ];

    fff = fopen("/proc/cpuinfo", "r");
    if (fff == NULL) return -1;

    while (1) {
        result = fgets(buffer, BUFSIZ, fff);
        if (result == NULL) break;

        if (!strncmp(result, "vendor_id", 9)) {
            sscanf(result, "%*s%*s%s", vendor);
            if (strncmp(vendor, "GenuineIntel", 12)) {
                fprintf(stderr, "[ERROR] %s is not an Intel chip\n", vendor);
                fclose(fff);
                return -1;
            }
        }

        if (!strncmp(result, "cpu family", 10)) {
            sscanf(result, "%*s%*s%*s%d", &family);
            if (family != 6) {
                fprintf(stderr, "[ERROR] Wrong CPU family %d\n", family);
                fclose(fff);
                return -1;
            }
        }

        if (!strncmp(result, "model", 5)) {
            sscanf(result, "%*s%*s%d", &model);
        }
    }

    fclose(fff);

    switch (model) {
        case CPU_SANDYBRIDGE:            printf("[INFO] Found Sandy Bridge CPU\n"); break;
        case CPU_SANDYBRIDGE_EP:         printf("[INFO] Found Sandy Bridge-EP CPU\n"); break;
        case CPU_IVYBRIDGE:              printf("[INFO] Found Ivy Bridge CPU\n"); break;
        case CPU_IVYBRIDGE_EP:           printf("[INFO] Found Ivy Bridge-EP CPU\n"); break;
        case CPU_HASWELL:                printf("[INFO] Found Haswell CPU\n"); break;
        case CPU_HASWELL_ULT:            printf("[INFO] Found Haswell ULT CPU\n"); break;
        case CPU_HASWELL_GT3E:           printf("[INFO] Found Haswell GT3E CPU\n"); break;
        case CPU_HASWELL_EP:             printf("[INFO] Found Haswell-EP CPU\n"); break;
        case CPU_BROADWELL:              printf("[INFO] Found Broadwell CPU\n"); break;
        case CPU_BROADWELL_GT3E:         printf("[INFO] Found Broadwell GT3E CPU\n"); break;
        case CPU_BROADWELL_EP:           printf("[INFO] Found Broadwell-EP CPU\n"); break;
        case CPU_BROADWELL_DE:           printf("[INFO] Found Broadwell-DE CPU\n"); break;
        case CPU_SKYLAKE:                printf("[INFO] Found Skylake CPU\n"); break;
        case CPU_SKYLAKE_HS:             printf("[INFO] Found Skylake-HS CPU\n"); break;
        case CPU_SKYLAKE_X:              printf("[INFO] Found Skylake-X CPU\n"); break;
        case CPU_KNIGHTS_LANDING:        printf("[INFO] Found Knights Landing CPU\n"); break;
        case CPU_KNIGHTS_MILL:           printf("[INFO] Found Knights Mill CPU\n"); break;
        case CPU_KABYLAKE_MOBILE:        printf("[INFO] Found Kaby Lake Mobile CPU\n"); break;
        case CPU_KABYLAKE:               printf("[INFO] Found Kaby Lake CPU\n"); break;
        case CPU_ATOM_SILVERMONT:        printf("[INFO] Found Atom Silvermont CPU\n"); break;
        case CPU_ATOM_AIRMONT:           printf("[INFO] Found Atom Airmont CPU\n"); break;
        case CPU_ATOM_MERRIFIELD:        printf("[INFO] Found Atom Merrifield CPU\n"); break;
        case CPU_ATOM_MOOREFIELD:        printf("[INFO] Found Atom Moorefield CPU\n"); break;
        case CPU_ATOM_GOLDMONT:          printf("[INFO] Found Atom Goldmont CPU\n"); break;
        case CPU_ATOM_GEMINI_LAKE:       printf("[INFO] Found Atom Gemini Lake CPU\n"); break;
        case CPU_ATOM_DENVERTON:         printf("[INFO] Found Atom Denverton CPU\n"); break;
        case CANNONLAKE_L:               printf("[INFO] Found Cannon Lake-L CPU\n"); break;
        case ICELAKE_L:                  printf("[INFO] Found Ice Lake-L CPU\n"); break;
        case ICELAKE:                    printf("[INFO] Found Ice Lake CPU\n"); break;
        case ICELAKE_D:                  printf("[INFO] Found Ice Lake-D CPU\n"); break;
        case ICELAKE_X:                  printf("[INFO] Found Ice Lake X CPU\n"); break;
        case COMETLAKE_L:                printf("[INFO] Found Comet Lake-L CPU\n"); break;
        case COMETLAKE:                  printf("[INFO] Found Comet Lake CPU\n"); break;
        case TIGERLAKE_L:                printf("[INFO] Found Tiger Lake-L CPU\n"); break;
        case TIGERLAKE:                  printf("[INFO] Found Tiger Lake CPU\n"); break;
        case ALDERLAKE:                  printf("[INFO] Found Alder Lake CPU\n"); break;
        case ALDERLAKE_L:                printf("[INFO] Found Alder Lake-L CPU\n"); break;
        case ALDERLAKE_N:                printf("[INFO] Found Alder Lake-N CPU\n"); break;
        case RAPTORLAKE:                 printf("[INFO] Found Raptor Lake CPU\n"); break;
        case RAPTORLAKE_P:               printf("[INFO] Found Raptor Lake-P CPU\n"); break;
        case RAPTORLAKE_S:               printf("[INFO] Found Raptor Lake-S CPU\n"); break;
        case METEORLAKE:                 printf("[INFO] Found Meteor Lake CPU\n"); break;
        case METEORLAKE_L:               printf("[INFO] Found Meteor Lake-L CPU\n"); break;
        case SAPPHIRERAPIDS_X:           printf("[INFO] Found Sapphire Rapids X CPU\n"); break;
        case EMERALDRAPIDS_X:            printf("[INFO] Found Emerald Rapids X CPU\n"); break;
        default:
            fprintf(stderr, "[ERROR] Unsupported CPU model %d\n", model);
            model = -1;
            break;
    }

    return model;
}

int rapl_init(int core) {
    int fd;
    uint64_t result;

    cpu_model = detect_cpu();
    if (cpu_model < 0) {
        printf("[ERROR] Unsupported CPU type\n");
        exit(EXIT_FAILURE);
    }

    fd = open_msr(core);
    result = read_msr(fd, MSR_RAPL_POWER_UNIT);
    close(fd);

    if (result == (uint64_t)-1) {
        fprintf(stderr, "[ERROR] Failed to read MSR_RAPL_POWER_UNIT\n");
        return -1;
    }

    power_units  = pow(0.5, (double)(result & 0xf));
    energy_units = pow(0.5, (double)((result >> 8) & 0x1f));
    time_units   = pow(0.5, (double)((result >> 16) & 0xf));

    return 0;
}

void show_power_info(int core) {
  int fd;
  uint64_t result;
  double thermal_spec_power, minimum_power, maximum_power, time_window;

  fd = open_msr(core);
  result = read_msr(fd, MSR_PKG_POWER_INFO);
  close(fd);

  if (result == (uint64_t)-1) return;

  thermal_spec_power = power_units * (double)(result & 0x7fff);
  printf("Package thermal spec: %.3fW\n", thermal_spec_power);

  minimum_power = power_units * (double)((result >> 16) & 0x7fff);
  printf("Package minimum power: %.3fW\n", minimum_power);

  maximum_power = power_units * (double)((result >> 32) & 0x7fff);
  printf("Package maximum power: %.3fW\n", maximum_power);

  time_window = time_units * (double)((result >> 48) & 0x7fff);
  printf("Package maximum time window: %.6fs\n", time_window);
}

void show_power_limit(int core) {
  int fd;
  uint64_t result;

  fd = open_msr(core);
  result = read_msr(fd, MSR_PKG_RAPL_POWER_LIMIT);
  close(fd);

  if (result == (uint64_t)-1) return;

  printf("Package power limits are %s\n", (result >> 63) ? "locked" : "unlocked");
  double pkg_power_limit_1 = power_units * (double)((result >> 0) & 0x7FFF);
  double pkg_time_window_1 = time_units * (double)((result >> 17) & 0x007F);
  printf("Package power limit #1: %.3fW for %.6fs (%s, %s)\n", pkg_power_limit_1, pkg_time_window_1,
         (result & (1ULL << 15)) ? "enabled" : "disabled",
         (result & (1ULL << 16)) ? "clamped" : "not_clamped");

  double pkg_power_limit_2 = power_units * (double)((result >> 32) & 0x7FFF);
  double pkg_time_window_2 = time_units * (double)((result >> 49) & 0x007F);
  printf("Package power limit #2: %.3fW for %.6fs (%s, %s)\n", pkg_power_limit_2, pkg_time_window_2,
         (result & (1ULL << 47)) ? "enabled" : "disabled",
         (result & (1ULL << 48)) ? "clamped" : "not_clamped");

  printf("\n");
}

int rapl_before(FILE *fp, int core) {
  int fd;
  uint64_t result;
  fd = open_msr(core);

  double acc_pkg_throttled_time, acc_pp0_throttled_time;
  int pp0_policy, pp1_policy;
  int flag = 1; // Assume all values are valid (non-negative)

  result = read_msr(fd, MSR_PKG_ENERGY_STATUS);
  package_before = (double)result * energy_units;
  if (package_before < 0) {
      fprintf(stderr, "[WARNING]: package_before is negative: %f\n", package_before);
      flag = -1;
  }

  result = read_msr(fd, MSR_PKG_PERF_STATUS);
  acc_pkg_throttled_time = (double)result * time_units;
  if (acc_pkg_throttled_time < 0) {
      fprintf(stderr, "[WARNING]: acc_pkg_throttled_time is negative: %f\n", acc_pkg_throttled_time);
      flag = -1;
  }

  result = read_msr(fd, MSR_PP0_ENERGY_STATUS);
  pp0_before = (double)result * energy_units;
  if (pp0_before < 0) {
      fprintf(stderr, "[WARNING]: pp0_before is negative: %f\n", pp0_before);
      flag = -1;
  }

  result = read_msr(fd, MSR_PP0_POLICY);
  pp0_policy = (int)result & 0x001f;

  result = read_msr(fd, MSR_PP0_PERF_STATUS);
  acc_pp0_throttled_time = (double)result * time_units;
  if (acc_pp0_throttled_time < 0) {
      fprintf(stderr, "[WARNING]: acc_pp0_throttled_time is negative: %f\n", acc_pp0_throttled_time);
      flag = -1;
  }

  result = read_msr(fd, MSR_PP1_ENERGY_STATUS);
  pp1_before = (double)result * energy_units;
  if (pp1_before < 0) {
      fprintf(stderr, "[WARNING]: pp1_before is negative: %f\n", pp1_before);
      flag = -1;
  }

  result = read_msr(fd, MSR_PP1_POLICY);
  pp1_policy = (int)result & 0x001f;

  result = read_msr(fd, MSR_DRAM_ENERGY_STATUS);
  dram_before = (double)result * energy_units;
  if (dram_before < 0) {
      fprintf(stderr, "[WARNING]: dram_before is negative: %f\n", dram_before);
      flag = -1;
  }

  close(fd);

  return flag;
}


int rapl_after(FILE *fp, int core) {
  int fd;
  uint64_t result;
  double pkg_diff = 0, pp0_diff = 0, pp1_diff = 0, dram_diff = 0;
  int has_negative = 0;

  fd = open_msr(core);

  result = read_msr(fd, MSR_PKG_ENERGY_STATUS);
  package_after = (double)result * energy_units;
  pkg_diff = package_after - package_before;
  if (pkg_diff < 0) {
      fprintf(stderr, "[WARNING]: pkg_diff is negative: %f\n", pkg_diff);
      has_negative = 1;
  }

  result = read_msr(fd, MSR_PP0_ENERGY_STATUS);
  pp0_after = (double)result * energy_units;
  pp0_diff = pp0_after - pp0_before;
  if (pp0_diff < 0) {
      fprintf(stderr, "[WARNING]: pp0_diff is negative: %f\n", pp0_diff);
      has_negative = 1;
  }

  result = read_msr(fd, MSR_PP1_ENERGY_STATUS);
  pp1_after = (double)result * energy_units;
  pp1_diff = pp1_after - pp1_before;
  if (pp1_diff < 0) {
      fprintf(stderr, "[WARNING]: pp1_diff is negative: %f\n", pp1_diff);
      has_negative = 1;
  }

  result = read_msr(fd, MSR_DRAM_ENERGY_STATUS);
  dram_after = (double)result * energy_units;
  dram_diff = dram_after - dram_before;
  if (dram_diff < 0) {
      fprintf(stderr, "[WARNING]: dram_diff is negative: %f\n", dram_diff);
      has_negative = 1;
  }
  
  close(fd);
  
  if (has_negative) {
      fprintf(stderr, "[ERROR]: Negative values detected - rapl_after().\n");
      return -1;
  }

  // Only log if all values are valid
  fprintf(fp, "%.18f, %.18f, %.18f, %.18f, ", pkg_diff, pp0_diff, pp1_diff, dram_diff);
  return 1;
}
