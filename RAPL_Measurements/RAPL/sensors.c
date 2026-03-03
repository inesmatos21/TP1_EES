#include "sensors.h"

float getTemperature() {
    // Robust one-liner: extracts all Core temps and averages them
    const char *cmd = "sensors | grep -E 'Core [0-9]+' | awk -F'+' '{split($2,a,\"°\"); sum+=a[1]} END {if(NR>0) print sum/NR; else print -1}'";

    FILE *fp = popen(cmd, "r");
    if (!fp) {
        perror("[ERROR] Failed to run sensors command");
        return -1.0f;
    }

    char buf[64];
    if (!fgets(buf, sizeof(buf), fp)) {
        perror("[ERROR] Failed to read sensors output");
        pclose(fp);
        return -1.0f;
    }

    pclose(fp);

    float avgTemp = atof(buf);
    printf("\n[INFO] Current average CPU temperature: %.2f°C\n", avgTemp);

    return avgTemp;
}

float getInitialTemperature() {
    FILE *file = fopen("/tmp/cores_temperatures.txt", "r");
    if (!file) {
        perror("[ERROR] Error opening file /tmp/cores_temperatures.txt");
        return -1;
    }

    char line[256];
    regex_t regex;
    regmatch_t matches[2];
    const char *pattern = "Average temperature: ([0-9]+\\.[0-9]+)°C";

    // Compile the regular expression
    if (regcomp(&regex, pattern, REG_EXTENDED) != 0) {
        fprintf(stderr, "[ERROR] Error compiling regex (getInitialTemperature())\n");
        fclose(file);
        return -1;
    }

    float result = -1.0;

    // Read lines from the file
    while (fgets(line, sizeof(line), file)) {
        if (regexec(&regex, line, 2, matches, 0) == 0) {
            // Extract the substring corresponding to the number
            char buffer[16];
            int start = matches[1].rm_so;
            int end = matches[1].rm_eo;
            snprintf(buffer, end - start + 1, "%s", line + start);
            result = atof(buffer);
            break;
        }
    }

    regfree(&regex);
    fclose(file);
    return result;
}