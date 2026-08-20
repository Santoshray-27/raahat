import 'dart:io';
import '../core/constants/enums.dart';

class NetworkService {
  static Future<NetworkMode> checkConnectivity() async {
    try {
      final result = await InternetAddress.lookup('google.com')
          .timeout(const Duration(seconds: 3));

      if (result.isNotEmpty && result[0].rawAddress.isNotEmpty) {
        return NetworkMode.ONLINE;
      }
    } on SocketException catch (_) {
      return NetworkMode.OFFLINE;
    } catch (_) {
      return NetworkMode.LIMITED;
    }

    return NetworkMode.OFFLINE;
  }
}