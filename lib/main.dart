import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:flutter/material.dart';

import 'firebase_options.dart';
import 'screens/auth_gate.dart';
import 'screens/dashboard_screen.dart';
import 'screens/new_plan_flow.dart';
import 'screens/placeholder_screen.dart';
import 'screens/plan_detail_screen.dart';
import 'screens/plans_screen.dart';
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
      onGenerateRoute: (settings) {
        if (settings.name == '/plan') {
          final id = settings.arguments as String?;
          if (id == null) {
            return MaterialPageRoute(
              builder: (_) => const PlansScreen(),
              settings: settings,
            );
          }
          return MaterialPageRoute(
            builder: (_) => PlanDetailScreen(planId: id),
            settings: settings,
          );
        }
        if (settings.name == '/new-plan') {
          final args = settings.arguments is NewPlanArgs
              ? settings.arguments as NewPlanArgs
              : null;
          return MaterialPageRoute(
            builder: (_) => NewPlanFlow(args: args),
            settings: settings,
          );
        }
        return null;
      },
      routes: {
        '/': (_) => const AuthGate(),
        '/dashboard': (_) => const DashboardScreen(),
        '/new-plan': (_) => const NewPlanFlow(),
        '/plans': (_) => const PlansScreen(),
        '/graph': (_) => const PlaceholderScreen(
              title: 'Knowledge Graph',
              description:
                  'The combined cognitive graph across all your plans, with '
                  'evidence, dependencies and uncertainty.',
              icon: Icons.hub_outlined,
              sidebarIndex: 3,
            ),
        '/scenarios': (_) => const PlaceholderScreen(
              title: 'Scenarios',
              description:
                  'What-if branches you can explore without changing your '
                  'main plan.',
              icon: Icons.layers_outlined,
              sidebarIndex: 4,
            ),
        '/documents': (_) => const PlaceholderScreen(
              title: 'Documents',
              description:
                  'Uploaded reports, briefs and data. Reflica extracts facts, '
                  'observations and constraints you can trace back.',
              icon: Icons.description_outlined,
              sidebarIndex: 5,
            ),
        '/settings': (_) => const PlaceholderScreen(
              title: 'Settings',
              description:
                  'Account, workspace, LLM provider, and governance preferences.',
              icon: Icons.settings_outlined,
              sidebarIndex: 6,
            ),
      },
    );
  }
}
