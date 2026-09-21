import 'dart:convert';
import 'dart:ui' show DartPluginRegistrant;

import 'package:flet/flet.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';
import 'package:geofencing_service/geofencing_service.dart';
import 'package:shared_preferences/shared_preferences.dart';

const _metadataKey = 'pioneiro_pro_geofence_metadata_v1';
const _lastEventKey = 'pioneiro_pro_geofence_last_event_v1';
const _channelId = 'pioneiro_pro_proximidade_nativa';
const _channelName = 'Avisos de proximidade';
const _channelDescription =
    'Avisos quando você entra na área de um estudante ou revisita cadastrada.';

int _notificationId(String regionId) {
  final parts = regionId.split(':');
  final numeric = parts.length > 1 ? int.tryParse(parts.last) ?? 1 : 1;
  return (regionId.startsWith('visita:') ? 20000 : 10000) + (numeric % 9000);
}

Future<Map<String, dynamic>> _readMetadata() async {
  final prefs = await SharedPreferences.getInstance();
  final raw = prefs.getString(_metadataKey);
  if (raw == null || raw.isEmpty) return <String, dynamic>{};

  final decoded = jsonDecode(raw);
  if (decoded is! Map) return <String, dynamic>{};
  return Map<String, dynamic>.from(decoded);
}

@pragma('vm:entry-point')
Future<void> pioneiroProGeofenceCallback(GeofenceTriggerEvent event) async {
  DartPluginRegistrant.ensureInitialized();

  if (event.type != GeofenceEventType.enter) return;

  final metadata = await _readMetadata();
  final prefs = await SharedPreferences.getInstance();

  const initSettings = InitializationSettings(
    android: AndroidInitializationSettings('@mipmap/ic_launcher'),
  );
  final notifications = FlutterLocalNotificationsPlugin();
  await notifications.initialize(settings: initSettings);

  const details = NotificationDetails(
    android: AndroidNotificationDetails(
      _channelId,
      _channelName,
      channelDescription: _channelDescription,
      importance: Importance.high,
      priority: Priority.high,
      category: AndroidNotificationCategory.reminder,
      autoCancel: true,
    ),
  );

  for (final regionId in event.regionIds) {
    final raw = metadata[regionId];
    final info = raw is Map
        ? Map<String, dynamic>.from(raw)
        : <String, dynamic>{};

    final nome = (info['nome'] as String?)?.trim();
    final titulo = (info['titulo'] as String?)?.trim();
    final bodyName = (nome == null || nome.isEmpty) ? 'Um contato' : nome;
    final notificationTitle =
        (titulo == null || titulo.isEmpty) ? 'Local próximo' : titulo;

    final payload = <String, dynamic>{
      'id': regionId,
      'tipo': info['tipo'] ?? '',
      'nome': bodyName,
      'titulo': notificationTitle,
      'latitude': info['latitude'],
      'longitude': info['longitude'],
      'timestamp': DateTime.now().toUtc().toIso8601String(),
    };
    await prefs.setString(_lastEventKey, jsonEncode(payload));

    await notifications.show(
      id: _notificationId(regionId),
      title: notificationTitle,
      body: '$bodyName está próximo. Toque para abrir o Pioneiro Pro.',
      notificationDetails: details,
      payload: jsonEncode(payload),
    );
  }
}

class PioneiroProGeofencingService extends FletService {
  PioneiroProGeofencingService({required super.control});

  bool _initialized = false;

  @override
  void init() {
    super.init();
    control.addInvokeMethodListener(_onMethod);
  }

  @override
  void dispose() {
    control.removeInvokeMethodListener(_onMethod);
    super.dispose();
  }

  Future<void> _ensureInitialized() async {
    if (_initialized) return;
    await FlutterGeofencePlugin.initialize(pioneiroProGeofenceCallback);
    _initialized = true;
  }

  Future<dynamic> _onMethod(String name, dynamic args) async {
    try {
      switch (name) {
        case 'initialize':
          await _ensureInitialized();
          return 'true';

        case 'request_permissions':
          await _ensureInitialized();
          final locationGranted =
              await FlutterGeofencePlugin.requestPermissions();

          const notificationSettings = InitializationSettings(
            android: AndroidInitializationSettings('@mipmap/ic_launcher'),
          );
          final notifications = FlutterLocalNotificationsPlugin();
          await notifications.initialize(settings: notificationSettings);
          final android = notifications.resolvePlatformSpecificImplementation<
              AndroidFlutterLocalNotificationsPlugin>();
          final notificationGranted =
              await android?.requestNotificationsPermission() ?? false;

          return (locationGranted && notificationGranted).toString();

        case 'registered_ids':
          await _ensureInitialized();
          return jsonEncode(
            await FlutterGeofencePlugin.getRegisteredGeofenceIds(),
          );

        case 'clear_regions':
          await _ensureInitialized();
          final ids = await FlutterGeofencePlugin.getRegisteredGeofenceIds();
          for (final id in ids) {
            await FlutterGeofencePlugin.removeGeofence(id);
          }
          final prefs = await SharedPreferences.getInstance();
          await prefs.remove(_metadataKey);
          return 'ok';

        case 'sync_regions':
          await _ensureInitialized();
          final params = Map<String, dynamic>.from(args as Map);
          final rawRegions = (params['regions'] as List<dynamic>? ?? const []);
          if (rawRegions.length > 100) {
            throw StateError(
              'Android permite no máximo 100 regiões monitoradas por aplicativo.',
            );
          }

          final desired = <String, Map<String, dynamic>>{};
          for (final raw in rawRegions) {
            final region = Map<String, dynamic>.from(raw as Map);
            final id = region['id'] as String;
            desired[id] = region;
          }

          final prefs = await SharedPreferences.getInstance();
          final previousRaw = prefs.getString(_metadataKey);
          final previousDecoded = previousRaw == null
              ? <String, dynamic>{}
              : jsonDecode(previousRaw);
          final previous = previousDecoded is Map
              ? Map<String, dynamic>.from(previousDecoded)
              : <String, dynamic>{};

          final registered =
              (await FlutterGeofencePlugin.getRegisteredGeofenceIds()).toSet();

          var added = 0;
          var updated = 0;
          var removed = 0;

          for (final id in registered.difference(desired.keys.toSet())) {
            await FlutterGeofencePlugin.removeGeofence(id);
            removed++;
          }

          for (final entry in desired.entries) {
            final id = entry.key;
            final region = entry.value;
            final oldRegion = previous[id];
            final unchanged =
                registered.contains(id) && jsonEncode(oldRegion) == jsonEncode(region);
            if (unchanged) continue;

            if (registered.contains(id)) {
              await FlutterGeofencePlugin.removeGeofence(id);
              updated++;
            } else {
              added++;
            }

            await FlutterGeofencePlugin.registerGeofence(
              GeofenceRegion(
                id: id,
                latitude: (region['latitude'] as num).toDouble(),
                longitude: (region['longitude'] as num).toDouble(),
                radiusMeters: (region['raio_m'] as num).toDouble(),
                triggers: const {GeofenceEventType.enter},
                initialTriggers: const <GeofenceEventType>{},
              ),
            );
          }

          await prefs.setString(_metadataKey, jsonEncode(desired));
          return jsonEncode({
            'total': desired.length,
            'added': added,
            'updated': updated,
            'removed': removed,
          });

        case 'is_background_restricted':
          await _ensureInitialized();
          return (await FlutterGeofencePlugin.isBackgroundRestricted()).toString();

        case 'is_ignoring_battery_optimizations':
          await _ensureInitialized();
          return (await FlutterGeofencePlugin.isIgnoringBatteryOptimizations())
              .toString();

        case 'consume_last_event':
          final prefs = await SharedPreferences.getInstance();
          final value = prefs.getString(_lastEventKey) ?? '';
          if (value.isNotEmpty) {
            await prefs.remove(_lastEventKey);
          }
          return value;
      }

      throw ArgumentError('unknown method: $name');
    } catch (e) {
      return 'error:${e.runtimeType}: $e';
    }
  }
}
