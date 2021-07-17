# How-to

## Determine a handler

e.g. VLC

1. Find an example file, right click, "Get Info", "Open with:", choose VLC, then "Change all..."
2. `duti -x mp4` shows that the handler is `org.videolan.vlc`.

## Determine kMDItemContentType

This will not work over samba:

1. Find an example file,
2. `mdls -name kMDItemContentType $FILENAME`

## List existing handlers

```bash
defaults read com.apple.LaunchServices/com.apple.launchservices.secure LSHandlers
```

## Dynamic type identifier

For those files that has Dynamic type identifier starting with `dyn.`, associate with file extension instead:


```bash
# default-open.sh
defaults write ~/Library/Preferences/com.apple.LaunchServices/com.apple.launchservices.secure.plist LSHandlers -array-add \
"{
    LSHandlerContentTag = ${ext};
    LSHandlerContentTagClass = 'public.filename-extension';
    LSHandlerPreferredVersions =             {
        LSHandlerRoleAll = '-';
    };
    LSHandlerRoleAll = 'com.microsoft.vscode';
}"
```

Note:

- Use UTI when available, and fall back to extension based method.
- Same method can actually be used for UTI as well. Consider migrating to this s.t. `duti` is not needed.

# References

- [System-Declared Uniform Type Identifiers](https://developer.apple.com/library/archive/documentation/Miscellaneous/Reference/UTIRef/Articles/System-DeclaredUniformTypeIdentifiers.html#//apple_ref/doc/uid/TP40009259-SW1)
- [moretension/duti: A command-line tool to select default applications for document types and URL schemes on Mac OS X](https://github.com/moretension/duti)
    - [duti documentation](http://duti.sourceforge.net/documentation.php)
- [ickc/apple-uti-data: Parse Apple UTI table to usable data structure and dump to YAML.](https://github.com/ickc/apple-uti-data)
