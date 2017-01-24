# VPortal Report Template generator

XML Report Template generator

- [INSTALLATION](#installation)
- [CONFIGURATION](#configuration)
- [OPTIONS](#options)
- [LOG](#log)


# INSTALLATION

To install it right away for all UNIX users (Linux, OS X, etc.), type:

    sudo apt-get install python3

To install python3 for CentOs/RHEL 5/6(not in repo):

    yum install xz-libs
    yum groupinstall -y 'development tools'
    yum install openssl-devel

    wget http://python.org/ftp/python/3.4.5/Python-3.4.5.tar.xz
    xz -d Python-3.4.5.tar.xz
    tar xvf Python-3.4.5.tar.xz
    cd Python-3.4.5
    sudo ./configure --prefix=/usr/local --enable-shared LDFLAGS="-Wl,-rpath /usr/local/lib"
    sudo make
    sudo make altinstall

To install python3 for CentOs/RHEL 7):

    yum install epel
    yum install python3

To install python3 for windows :

    Install python3 installer (https://www.python.org/downloads/)

# CONFIGURATION

Setting up input files :

    Create input csv file with line containing the below data input:
    # List of indicators, wid, drill_down report, unit
    # Format: <Indicator display NAME>,<WID>,<drill down report path>,unit
    # Example: Speech CSSR,372D613D9C2611E698E80A093D181D13,"Customized/Raw Counters/Geocell - Speech CSSR Raw Counters",%
    # Optional:
    # Threshold definition is supported using config file threshold.ini
    # First column define order of threshold UP or DOWN
    # All other columns can be used for threshold
    # Example: Speech CSSR,372D613D9C2611E698E80A093D181D13,"Customized/Raw Counters/Geocell - Speech CSSR Raw Counters",%,DOWN,K1-CRIT
    # Read parameter from threshold.init where K1-CRIT is defined as below: 
    [K1-CRIT]
    property = E20A2280AFE711E68B050050569240C5
    icon = circlelight_red_4x.gif

Defining options.ini parameter :
    
    options.ini file allow to define global options
    [DEFAULT]
    VP_VERSION = 5.1 => VP Version
    BUILD_NUMBER = 51029 => VP Build number
    [DEFAULT-UP]
    icon = circlelight_red_a_4x.gif => Default icon to be used in threshold if order is UP
    [DEFAULT-DOWN]
    icon = circlelight_red_a_4x.gif => Default icon to be used in threshold if order is DOWN
    
    
# OPTIONS

    usage: vp_generator.py [-i] [-o] [-v] [-m] [-h]
        Parse and generate Report Template xml file based on input data file:
        Options:
        -h, --help            show this help message and exit
        -i FILE, --input=FILE
            Input file containing NAME,WID,Drill-down path
        -o FILE, --output=FILE
            Specify output xml file name, default path: output.xml
        -m MODE, --mode=MODE  Specify mode : normal or temporal, default: normal
        -v, --verbose         Enable debug mode


# LOG
    all log are stored under file name vp_generator.log in script folder