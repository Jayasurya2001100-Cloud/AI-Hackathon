import 'dart:convert';
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:image_picker/image_picker.dart';
import 'package:speech_to_text/speech_to_text.dart' as stt;
import 'package:flutter_tts/flutter_tts.dart';
import 'package:permission_handler/permission_handler.dart';

void main() {
  runApp(const PestDetectionApp());
}

class PestDetectionApp extends StatelessWidget {
  const PestDetectionApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'Pest Detection',
      theme: ThemeData(
        primarySwatch: Colors.deepPurple,
        elevatedButtonTheme: ElevatedButtonThemeData(
          style: ElevatedButton.styleFrom(
            padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 14),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(14),
            ),
          ),
        ),
        textTheme: const TextTheme(
          bodyLarge: TextStyle(fontSize: 18),
          titleLarge: TextStyle(fontWeight: FontWeight.bold, fontSize: 22),
        ),
      ),
      home: const PestDetectionPage(),
    );
  }
}

class PestDetectionPage extends StatefulWidget {
  const PestDetectionPage({super.key});

  @override
  State<PestDetectionPage> createState() => _PestDetectionPageState();
}

class _PestDetectionPageState extends State<PestDetectionPage> {
  final ImagePicker _picker = ImagePicker();
  final stt.SpeechToText _speech = stt.SpeechToText();
  final FlutterTts _flutterTts = FlutterTts();

  bool _isListening = false;
  bool _isLoading = false;
  String _speechText = "";
  String _prediction = "";

  final String backendUrl = "http://127.0.0.1:8000/predict-image/";


  @override
  void initState() {
    super.initState();
    _initSpeech();
    _requestPermissions();
  }

  Future<void> _requestPermissions() async {
    await [Permission.microphone, Permission.camera].request();
  }

  void _initSpeech() async {
    bool available = await _speech.initialize();
    if (!available) {
      debugPrint("Speech recognition not available");
    }
  }

  Future<void> _pickImage(ImageSource source) async {
    final XFile? image = await _picker.pickImage(source: source);
    if (image != null) {
      setState(() {
        _isLoading = true;
        _prediction = "Analyzing image...";
      });

      final bytes = await image.readAsBytes();
      var request = http.MultipartRequest('POST', Uri.parse('$backendUrl/predict-image/'));
      request.files.add(http.MultipartFile.fromBytes('file', bytes, filename: 'pest.jpg'));

      try {
        var response = await request.send();
        if (response.statusCode == 200) {
          final respStr = await response.stream.bytesToString();
          final jsonResp = json.decode(respStr);
          setState(() {
            _prediction = "Pest: ${jsonResp['pest']}\nConfidence: ${(jsonResp['confidence'] * 100).toStringAsFixed(1)}%";
          });
          _speak(_prediction);
        } else {
          setState(() => _prediction = "Failed to predict. Please try again.");
        }
      } catch (e) {
        setState(() => _prediction = "Error: $e");
      } finally {
        setState(() => _isLoading = false);
      }
    }
  }

  void _speak(String text, {String lang = "en-US"}) async {
    await _flutterTts.setLanguage(lang);
    await _flutterTts.speak(text);
  }

  void _startListening() async {
    if (!_isListening) {
      bool available = await _speech.initialize();
      if (available) {
        setState(() => _isListening = true);
        _speech.listen(
          onResult: (val) => setState(() {
            _speechText = val.recognizedWords;
          }),
          localeId: "en_US",
        );
      }
    }
  }

  void _stopListening() async {
    await _speech.stop();
    setState(() => _isListening = false);
    _sendSpeechToBackend(_speechText);
  }

  void _sendSpeechToBackend(String speech) async {
    setState(() => _prediction = "You said: $speech");
    _speak(_prediction);
    if (speech.toLowerCase().contains("capture")) {
      Future.delayed(const Duration(seconds: 1), () => _pickImage(ImageSource.camera));
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Pest Detection', style: TextStyle(fontWeight: FontWeight.bold)),
        centerTitle: true,
      ),
      body: Container(
        padding: const EdgeInsets.all(20),
        color: Colors.grey.shade100,
        child: SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Card(
                elevation: 6,
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                child: Padding(
                  padding: const EdgeInsets.all(20.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text("Upload Image", style: Theme.of(context).textTheme.titleLarge),
                      const SizedBox(height: 16),
                      ElevatedButton.icon(
                        onPressed: _isLoading ? null : () => _pickImage(ImageSource.camera),
                        icon: Icon(Icons.camera_alt_rounded), // ✅ Proper Icon widget
                        label: Text('📸 Capture Pest Image'),  // ✅ Emoji inside text only
                        style: ElevatedButton.styleFrom(
                          backgroundColor: Colors.deepPurple,
                          foregroundColor: Colors.white,
                        ),
                      ),

                      ElevatedButton.icon(
                          onPressed: _isLoading ? null : () => _pickImage(ImageSource.gallery),
                          icon: Icon(Icons.photo_library_outlined),
                          label: Text('🖼️ Pick from Gallery'),
                          style: ElevatedButton.styleFrom(
                            backgroundColor: Colors.deepPurple,
                            foregroundColor: Colors.white,
                          )
                        ),

                        ElevatedButton.icon(
                          onPressed: _isListening ? _stopListening : _startListening,
                          icon: Icon(_isListening ? Icons.stop : Icons.mic),
                          label: Text(_isListening ? '🛑 Stop Listening' : '🎤 Start Voice Input'),
                          style: ElevatedButton.styleFrom(
                            backgroundColor: Colors.deepPurple,
                            foregroundColor: Colors.white,
                          ),
                        ),

                    ],                     
                  ),
                ),
              ),
              const SizedBox(height: 20),
              if (_isLoading) const Center(child: CircularProgressIndicator()),
              if (!_isLoading)
                Card(
                  elevation: 4,
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                  color: Colors.white,
                  child: Padding(
                    padding: const EdgeInsets.all(16),
                    child: Text(
                      _prediction.isNotEmpty ? _prediction : "No result yet.",
                      style: const TextStyle(fontSize: 18, color: Colors.black87),
                      textAlign: TextAlign.center,
                    ),
                  ),
                ),
              const SizedBox(height: 30),
              Text("Voice Command", style: Theme.of(context).textTheme.titleLarge),
              const SizedBox(height: 10),
              ElevatedButton.icon(
                onPressed: _isListening ? _stopListening : _startListening,
                icon: Icon(_isListening ? Icons.stop : Icons.mic),
                label: Text(_isListening ? 'Stop Listening' : 'Start Voice Input'),
              ),
              const SizedBox(height: 12),
              Text(
                _speechText.isNotEmpty ? '"$_speechText"' : 'Voice input will appear here.',
                style: const TextStyle(fontSize: 16, color: Colors.black54),
                textAlign: TextAlign.center,
              ),
            ],
          ),
        ),
      ),
    );
  }
}
