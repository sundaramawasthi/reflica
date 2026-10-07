import 'dart:async';

import 'package:firebase_auth/firebase_auth.dart' as fb;
import 'package:firebase_core/firebase_core.dart';
import 'package:flutter/foundation.dart';
import 'package:google_sign_in/google_sign_in.dart';

/// Thrown by [AuthService.signInWithGoogle] with a message safe to show in
/// the UI. [code] is set when we know the underlying Firebase/network cause.
class SignInException implements Exception {
  final String message;
  final String? code;
  const SignInException(this.message, {this.code});

  bool get isNetwork => code == 'network' || code == 'network-request-failed';
  bool get isCancelled =>
      code == 'user-cancelled' ||
      code == 'canceled' ||
      code == 'web-context-cancelled' ||
      code == 'popup-closed-by-user';

  @override
  String toString() => message;
}

/// Lightweight user shape the UI binds to.
/// Backed by [fb.User] when Firebase is initialised, otherwise by a stub.
class AppUser {
  final String uid;
  final String? displayName;
  final String? email;
  final String? photoURL;
  const AppUser({
    required this.uid,
    this.displayName,
    this.email,
    this.photoURL,
  });

  factory AppUser.fromFirebase(fb.User u) => AppUser(
        uid: u.uid,
        displayName: u.displayName,
        email: u.email,
        photoURL: u.photoURL,
      );
}

class AuthService {
  AuthService._();
  static final instance = AuthService._();

  // Demo-mode (no Firebase) state ---------------------------------------------
  final _demoController = StreamController<AppUser?>.broadcast();
  AppUser? _demoUser;

  bool get isDemoMode => Firebase.apps.isEmpty;

  Stream<AppUser?> get authState {
    if (isDemoMode) {
      return _demoController.stream;
    }
    return fb.FirebaseAuth.instance
        .authStateChanges()
        .map((u) => u == null ? null : AppUser.fromFirebase(u));
  }

  AppUser? get currentUser {
    if (isDemoMode) return _demoUser;
    final u = fb.FirebaseAuth.instance.currentUser;
    return u == null ? null : AppUser.fromFirebase(u);
  }

  // The project's **web** OAuth client id from google-services.json — needed
  // by google_sign_in on Android so the ID token is valid for Firebase.
  static const _serverClientId =
      '53064442729-mnva30m81sr31010lss08uidrlcpshen.apps.googleusercontent.com';

  // Shared GoogleSignIn instance so signIn + signOut operate on the same
  // native session on Android / iOS.
  GoogleSignIn? _gs;
  GoogleSignIn get _googleSignIn => _gs ??= GoogleSignIn(
        scopes: const ['email', 'profile'],
        serverClientId: _serverClientId,
      );

  Future<void> signInWithGoogle() async {
    if (isDemoMode) {
      _demoUser = const AppUser(
        uid: 'demo',
        displayName: 'Demo User',
        email: 'demo@reflica.local',
      );
      _demoController.add(_demoUser);
      return;
    }

    try {
      if (kIsWeb) {
        // On web, Firebase's popup is already an in-page overlay.
        final provider = fb.GoogleAuthProvider()
          ..addScope('email')
          ..addScope('profile')
          ..setCustomParameters({'prompt': 'select_account'});
        await fb.FirebaseAuth.instance.signInWithPopup(provider);
      } else {
        // Android / iOS: use google_sign_in — shows the account picker as an
        // in-app bottom sheet instead of opening a separate activity. Then
        // we feed the ID + access tokens into Firebase Auth.
        final gs = _googleSignIn;
        // Force the account chooser each time, mirroring the web popup UX.
        await gs.signOut();
        final account = await gs.signIn();
        if (account == null) {
          throw const SignInException('Sign-in cancelled.', code: 'canceled');
        }
        final auth = await account.authentication;
        final credential = fb.GoogleAuthProvider.credential(
          idToken: auth.idToken,
          accessToken: auth.accessToken,
        );
        await fb.FirebaseAuth.instance.signInWithCredential(credential);
      }
    } on SignInException {
      rethrow;
    } on fb.FirebaseAuthException catch (e) {
      // Translate Firebase codes + inner network errors into messages the UI
      // can show the user directly.
      final msg = _friendlyError(e);
      throw SignInException(msg, code: e.code);
    } catch (e) {
      final s = e.toString();
      if (s.contains('No address associated with hostname') ||
          s.contains('Unable to resolve host') ||
          s.contains('SocketException') ||
          s.contains('network-request-failed')) {
        throw const SignInException(
          'No internet connection. Connect to Wi-Fi or mobile data and try again.',
          code: 'network',
        );
      }
      throw SignInException('Sign-in failed: $e');
    }
  }

  String _friendlyError(fb.FirebaseAuthException e) {
    switch (e.code) {
      case 'network-request-failed':
        return 'No internet connection. Connect to Wi-Fi or mobile data and try again.';
      case 'user-disabled':
        return 'This account has been disabled.';
      case 'account-exists-with-different-credential':
        return 'An account already exists with a different sign-in method.';
      case 'invalid-credential':
        return 'The sign-in credential is no longer valid. Try again.';
      case 'operation-not-allowed':
        return 'Google sign-in is not enabled for this project yet.';
      case 'user-cancelled':
      case 'web-context-cancelled':
      case 'canceled':
        return 'Sign-in cancelled.';
      case 'popup-closed-by-user':
        return 'The Google sign-in window was closed before finishing.';
      case 'popup-blocked':
        return 'The sign-in popup was blocked by the browser. Allow popups and try again.';
      case 'too-many-requests':
        return 'Too many sign-in attempts. Try again in a few minutes.';
      default:
        return e.message ?? 'Sign-in failed (${e.code}).';
    }
  }

  Future<void> signOut() async {
    if (isDemoMode) {
      _demoUser = null;
      _demoController.add(null);
      return;
    }
    // Clear native Google session too so the account picker reappears next
    // time instead of silently re-signing in with the last account. Use the
    // shared GoogleSignIn instance so we actually clear THIS user, and
    // disconnect() in addition to signOut() so Credential Manager fully
    // forgets us on Android.
    if (!kIsWeb) {
      try {
        final gs = _googleSignIn;
        try {
          await gs.disconnect();
        } catch (_) {
          // disconnect may fail if the user already revoked access; ignore.
        }
        await gs.signOut();
      } catch (_) {
        // Non-fatal — proceed to Firebase sign-out anyway.
      }
    }
    await fb.FirebaseAuth.instance.signOut();
  }
}
