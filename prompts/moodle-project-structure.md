
local_pluginB/
│
├── db/                       # Database scripts and events
│   ├── install.xml           # XML schema for installation
│   ├── upgrade.php           # Upgrade script
│   ├── access.php            # Permissions and capabilities
│   └── events.php            # Event observers
│
├── lang/                     # Language files for localization
│   └── en/
│       └── local_pluginb.php # English language strings
│
├── lib.php                   # Plugin-specific library functions
├── version.php               # Plugin metadata and version info
├── settings.php              # Admin settings (optional)
├── index.php                 # Plugin main page, if applicable
├── classes/                  # Namespaced PHP classes
│   └── ...                   # Organized by functionality
├── templates/                # Mustache templates for UI rendering
│   └── ... 
├── pix/                      # Plugin images and icons
│   └── ...
├── amd/                      # JavaScript modules (AMD style)
│   └── ...
├── README.md                 # Documentation for this plugin
├── LICENSE                   # License information
└── tests/                    # PHPUnit/Behat test cases
    └── ...

    Moodle and PHP location details :
    OS : Windows 11
    Database : Postgres as per standard credentials and db name on local
    Xampp location : D:\xampp
    moodle folder : D:\xampp\moodle