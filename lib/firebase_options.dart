import 'package:firebase_core/firebase_core.dart' show FirebaseOptions;
import 'package:flutter/foundation.dart'
    show defaultTargetPlatform, kIsWeb, TargetPlatform;

class DefaultFirebaseOptions {
  static FirebaseOptions get currentPlatform {
    if (kIsWeb) {
      return web;
    }
    switch (defaultTargetPlatform) {
      case TargetPlatform.android:
        return android;
      case TargetPlatform.iOS:
        throw UnsupportedError(
          'iOS is not configured for Firebase yet — register an iOS app in '
          'the reflica-593b4 Firebase console and add its options here.',
        );
      default:
        throw UnsupportedError(
          '${defaultTargetPlatform.name} is not supported by this app.',
        );
    }
  }

  static const FirebaseOptions web = FirebaseOptions(
    apiKey: 'AIzaSyBKPedCqeN_0cHkerB2dZ1MB5ntp8XZF7U',
    appId: '1:53064442729:web:085dd42d540e7d5aed93f8',
    messagingSenderId: '53064442729',
    projectId: 'reflica-593b4',
    authDomain: 'reflica-593b4.firebaseapp.com',
    databaseURL: 'https://reflica-593b4-default-rtdb.firebaseio.com',
    storageBucket: 'reflica-593b4.firebasestorage.app',
    measurementId: 'G-PGLLEQEB7G',
  );

  static const FirebaseOptions android = FirebaseOptions(
    apiKey: 'AIzaSyB4ygY5i4MKPUQ9pR-T1daTRgXmOrqq7dU',
    appId: '1:53064442729:android:d52f445c0e45941aed93f8',
    messagingSenderId: '53064442729',
    projectId: 'reflica-593b4',
    databaseURL: 'https://reflica-593b4-default-rtdb.firebaseio.com',
    storageBucket: 'reflica-593b4.firebasestorage.app',
  );
}
