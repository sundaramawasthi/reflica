import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:flutter/material.dart';

import 'firebase_options.dart';
import 'screens/auth_gate.dart';
import 'screens/dashboard_screen.dart';
import 'screens/placeholder_screen.dart';
import 'theme/app_theme.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();

  try {
    await Firebase.initializeApp(
      options: DefaultFirebaseOptions.currentPlatform,
    );
    // Explicitly enable offline persistence with an unlimited cache so that
    // writes made offline (e.g. a plan deletion while the phone has no
    // internet) survive logout + login and sync when the device reconnects.
    FirebaseFirestore.instance.settings = const Settings(
      persistenceEnabled: true,
      cacheSizeBytes: Settings.CACHE_SIZE_UNLIMITED,
    );
  } catch (e) {
    debugPrint('[Reflica] Firebase not initialised on this platform: $e');
    debugPrint('[Reflica] Running in demo mode (no real auth).');
  }
  runApp(const ReflicaApp());
}

class ReflicaApp extends StatelessWidget {
  const ReflicaApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Reflica',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.light(),
      initialRoute: '/',
      routes: {
        '/': (_) => const AuthGate(),
        '/dashboard': (_) => const DashboardScreen(),
        '/settings': (_) => const PlaceholderScreen(
              title: 'Settings',
              description: 'Account and display preferences.',
              icon: Icons.settings_outlined,
              sidebarIndex: 1,
            ),
      },
    );
  }
}
