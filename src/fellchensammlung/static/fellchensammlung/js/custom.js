function ifdef(variable, prefix = "", suffix = "") {
    if (variable !== undefined) {
        return prefix + variable + suffix;
    } else {
        return "";
    }

}