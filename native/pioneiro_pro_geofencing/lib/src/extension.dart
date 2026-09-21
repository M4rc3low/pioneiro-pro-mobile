import 'package:flet/flet.dart';

import 'geofencing_bridge_service.dart';

class Extension extends FletExtension {
  @override
  FletService? createService(Control control) {
    switch (control.type) {
      case "pioneiro_pro_geofencing":
        return PioneiroProGeofencingService(control: control);
      default:
        return null;
    }
  }
}
