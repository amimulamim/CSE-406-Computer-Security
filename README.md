# CSE-406 Computer Security

A comprehensive collection of practical implementations, assignments, and solutions for CSE-406 Computer Security course. This repository covers four major areas of computer security: Buffer Overflow Attacks, Cryptography, Ethical Hacking, and Side Channel Attacks.

## 📚 Repository Contents

This repository is organized into four main sections, each focusing on a critical aspect of computer security:

### 1. 🛡️ [Buffer Overflow Attack](./Buffer%20Overflow%20Attack)

Practical examples and solutions demonstrating buffer overflow vulnerabilities and exploitation techniques.

#### Contents:
- **Batch-20 Onlines + Solutions**: Current batch assignments and their solutions
  - **A1**: Buffer overflow exploitation with stack canaries
  - **A2**: Advanced buffer overflow techniques
  - **B1**: Basic buffer overflow vulnerability analysis
  - **B2**: Complex buffer overflow scenarios

- **Previous-Onlines + Solutions**: Historical assignments from Batch-19 for reference and practice

- **Buffer_Overflow_Resources**: Additional learning materials and resources

#### Key Concepts Covered:
- Stack-based buffer overflows
- Return-oriented programming (ROP)
- Stack canaries and bypass techniques
- Shellcode injection
- Address space layout randomization (ASLR)
- Exploit development and debugging

#### Example Attack Vector:
```c
void vuln(char *user, char *pass) {
    char buf[SZ];
    strcpy(buf, pass);  // Vulnerable strcpy without bounds checking
}
```

#### Technologies:
- C/C++ programming
- GDB debugger
- Assembly language (x86/x64)
- Linux security mechanisms

---

### 2. 🔐 [Cryptography](./Cryptography)

Implementation of modern cryptographic algorithms and secure communication protocols.

#### Contents:
- **Offline-1**: Complete AES and ECDH implementation
  - AES (Advanced Encryption Standard) implementation
    - Block cipher modes: ECB, CBC, CTR
    - Key schedule generation
    - S-Box and Inverse S-Box operations
    - MixColumns transformation
  - ECDH (Elliptic Curve Diffie-Hellman) key exchange
    - Elliptic curve point arithmetic
    - Secure key generation and exchange
    - Prime field operations
  - Client-server secure file transfer
  - Hash functions and message authentication

- **bitvector-demo.py**: Demonstration of BitVector operations for AES

#### Key Features:
- **AES Implementation**:
  - Multiple modes of operation (ECB, CBC, CTR)
  - PKCS7 padding scheme
  - Key scheduling algorithm
  - Galois Field arithmetic (GF(2^8))
  
- **ECDH Key Exchange**:
  - Prime field elliptic curve operations
  - Secure random number generation
  - Point multiplication and addition
  - Shared secret derivation

- **Secure Communication**:
  - Socket-based client-server architecture
  - File encryption and decryption
  - SHA-256 hashing
  - Performance benchmarking

#### Dependencies:
```
# See Cryptography/Offline-1/requirements.txt for exact versions
BitVector>=3.5.0        # For AES operations
sympy>=1.12             # For prime generation
pycryptodome>=3.19.0    # For cryptographic utilities
```

#### Architecture:
```
Client                          Server
  │                               │
  ├──► ECDH Key Exchange ────────┤
  │    (Public key sharing)       │
  │                               │
  ├──► Derive Shared Secret ─────┤
  │    (Private key mixing)       │
  │                               │
  ├──► AES-CTR Encrypted Data ───►
  │    (Secure file transfer)     │
  │                               │
  └──► SHA-256 Hash ─────────────►
       (Data integrity check)     │
```

---

### 3. 🎯 [Ethical Hacking](./Ethical%20Hacking)

Practical demonstrations of SQL injection techniques and web application security testing using WebGoat.

#### Contents:
- **SQL Injection Scripts**:
  - `timing_sqli.py`: Time-based blind SQL injection
  - `password_blindsqli.py`: Blind SQL injection for password extraction
  - `full_ip_extraction.py`: IP address extraction via SQL injection
  - `ip_mitigation.py`: SQL injection mitigation techniques demonstration

- **WebGoat Integration**:
  - `run_webgoat.sh`: Docker-based WebGoat deployment script
  - `cookie.py`: Session cookie management
  - `lesson/`: WebGoat lesson-specific materials

#### SQL Injection Techniques:

**1. Time-Based Blind SQL Injection**:
```python
# Testing character at position with timing delay
inj = (
    "CASE WHEN "
    f"substring((SELECT ip FROM servers WHERE hostname='webgoat-prd'),{pos},1)='{ch}' "
    f"THEN (SELECT SLEEP({delay})) "
    "ELSE hostname END"
)
```

**2. Boolean-Based Blind SQL Injection**:
- Character-by-character data extraction
- Binary search optimization
- Response analysis for true/false conditions

**3. IP Extraction**:
- Automated data exfiltration
- Pattern matching and validation
- Multi-database support (MySQL, PostgreSQL)

#### WebGoat Setup:
```bash
# Start WebGoat container
./run_webgoat.sh

# Access WebGoat UI
# http://127.0.0.1:8080/WebGoat

# Admin interface
# http://127.0.0.1:9090
```

#### Key Learning Objectives:
- Understanding SQL injection vulnerabilities
- Exploiting time-based and blind SQL injection
- Bypassing input validation and filters
- Implementing proper parameterized queries
- Security testing methodologies
- Responsible disclosure practices

#### Security Considerations:
⚠️ **Educational Purpose Only**: These tools are for learning and authorized security testing only. Unauthorized access to systems is illegal and unethical.

---

### 4. 🔬 [Side Channel Attack](./Side%20Channel%20Attack)

Advanced implementation of side-channel attacks for website fingerprinting using cache timing analysis and machine learning.

#### Complete Project Description:
This section contains a comprehensive implementation of website fingerprinting through side-channel attacks. For detailed documentation, see the [Side Channel Attack README](./Side%20Channel%20Attack/starter_code/template/README.md).

#### Quick Overview:
- **Technique**: Browser cache timing side-channel attacks
- **Goal**: Identify visited websites from timing patterns
- **Method**: Machine learning classification of timing traces
- **Live Demo**: [http://20.40.60.232:5000](http://20.40.60.232:5000) 
  - Educational deployment on Azure (demonstration purposes only)
  - Note: HTTP used for compatibility with browser timing APIs; not for production use

#### Key Components:

**Data Collection**:
- Automated Chrome browser control via Selenium
- Cache timing measurement using JavaScript
- 2000+ traces per website
- Multi-channel side-channel analysis

**Machine Learning Models**:
- Basic Classifier (85.2% accuracy)
- Complex Fingerprint Classifier (92.7% accuracy)
- Attention-Based Classifier (90.1% accuracy)
- Residual Network (91.8% accuracy)
- Adversarial Classifier (89.3% accuracy)
- Ensemble Classifier (94.1% accuracy)

**Web Interface**:
- Real-time website fingerprinting
- Interactive visualization dashboard
- Model performance comparison
- Heatmap generation for trace analysis

#### Quick Start:
```bash
cd "Side Channel Attack/starter_code/template"

# Install dependencies
pip install -r requirements.txt

# Collect data
python collect.py --traces 500

# Train models
python train.py --models all

# Start web interface
python app.py
# Visit http://localhost:5000
```

#### Resources:
- 📊 [Dataset on Kaggle](https://www.kaggle.com/datasets/amimulehsan1/side-channel-attack-2005017)
- 🤖 [Pre-trained Models](https://www.kaggle.com/models/amimulehsan1/side-channel-attacksweep-count)
- 🚀 [Live Demo](http://20.40.60.232:5000)

---

## 🚀 Getting Started

### Prerequisites

- **Python**: 3.10+ (see `runtime.txt` in each directory for specific versions)
  - Main repository: Python 3.12.7
  - Side Channel Attack: Python 3.10.10
- **C/C++ Compiler**: GCC for buffer overflow exercises
- **Docker**: For WebGoat and side-channel attack deployment
- **Chrome/Chromium**: For side-channel attack data collection

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/amimulamim/CSE-406-Computer-Security.git
   cd CSE-406-Computer-Security
   ```

2. **Set up for specific sections**:

   **For Cryptography**:
   ```bash
   cd Cryptography/Offline-1
   pip install -r requirements.txt
   python server.py  # In one terminal
   python client.py  # In another terminal
   ```

   **For Ethical Hacking**:
   ```bash
   cd "Ethical Hacking"
   ./run_webgoat.sh  # Start WebGoat
   # Then run SQL injection scripts
   python timing_sqli.py
   ```

   **For Side Channel Attack**:
   ```bash
   cd "Side Channel Attack/starter_code/template"
   pip install -r requirements.txt
   python app.py
   ```

   **For Buffer Overflow**:
   ```bash
   cd "Buffer Overflow Attack/Batch-20_Onlines+Solutions/A1"
   # Compile with security features disabled FOR EDUCATIONAL PURPOSES ONLY
   # WARNING: These flags disable critical security protections:
   #   -fno-stack-protector: Disables stack canaries
   #   -z execstack: Makes stack executable
   # NEVER use these flags in production code!
   gcc -fno-stack-protector -z execstack -o vuln A1.c
   ```

---

## 📖 Course Topics Covered

### Security Fundamentals
- Threat modeling and risk assessment
- Defense in depth strategies
- Secure coding practices
- Vulnerability analysis

### Exploitation Techniques
- Memory corruption vulnerabilities
- Web application attacks
- Cryptographic attacks
- Side-channel information leakage

### Defensive Mechanisms
- Stack canaries and ASLR
- Input validation and sanitization
- Secure cryptographic implementations
- Side-channel attack mitigations

### Applied Cryptography
- Symmetric encryption (AES)
- Key exchange protocols (ECDH)
- Hash functions and message authentication
- Secure communication protocols

---

## 🔒 Security & Ethics

### Responsible Use Guidelines

This repository contains powerful security tools and techniques. Users must:

✅ **DO**:
- Use for educational purposes and authorized testing
- Practice in isolated lab environments
- Follow responsible disclosure for vulnerabilities
- Respect privacy and legal boundaries
- Learn defensive security measures

❌ **DON'T**:
- Attack systems without explicit authorization
- Use for malicious purposes or personal gain
- Violate privacy or data protection laws
- Share sensitive information obtained through testing
- Exploit vulnerabilities in production systems

### Legal Notice

⚠️ **Disclaimer**: All materials in this repository are for educational purposes only. Unauthorized access to computer systems is illegal. Users are responsible for ensuring their activities comply with applicable laws and regulations. The authors and contributors are not responsible for any misuse of these materials.

---

## 📁 Repository Structure

```
CSE-406-Computer-Security/
│
├── Buffer Overflow Attack/
│   ├── Batch-20_Onlines+Solutions/    # Current assignments (A1, A2, B1, B2)
│   ├── Previous-Onlines+Solutions/    # Historical references (Batch-19)
│   └── Buffer_Overflow_Resources/     # Additional materials
│
├── Cryptography/
│   ├── Offline-1/                     # AES & ECDH implementation
│   │   ├── aes_*.py                   # AES cipher components
│   │   ├── ecdh_*.py                  # ECDH key exchange
│   │   ├── client.py & server.py     # Secure communication
│   │   └── requirements.txt
│   └── bitvector-demo.py              # BitVector operations demo
│
├── Ethical Hacking/
│   ├── timing_sqli.py                 # Time-based SQL injection
│   ├── password_blindsqli.py          # Blind SQL injection
│   ├── full_ip_extraction.py          # Data exfiltration
│   ├── ip_mitigation.py               # Mitigation techniques
│   ├── run_webgoat.sh                 # WebGoat deployment
│   └── lesson/                        # WebGoat materials
│
├── Side Channel Attack/
│   ├── specification.pdf              # Project specification
│   └── starter_code/template/         # Complete implementation
│       ├── collect.py                 # Data collection
│       ├── train.py                   # Model training
│       ├── app.py                     # Web interface
│       ├── requirements.txt
│       └── README.md                  # Detailed documentation
│
├── runtime.txt                        # Python version specification
├── .gitignore                         # Git ignore rules
└── README.md                          # This file
```

---

## 🛠️ Technologies Used

### Programming Languages
- **Python 3.12+**: Main language for cryptography, ethical hacking, and machine learning
- **C/C++**: Buffer overflow vulnerabilities and exploitation
- **JavaScript**: Browser-based side-channel attacks
- **Bash**: Automation scripts

### Frameworks & Libraries
- **PyTorch**: Deep learning for website fingerprinting
- **Flask**: Web interface for demonstrations
- **Selenium**: Browser automation for data collection
- **BitVector**: Cryptographic operations
- **Requests**: HTTP client for SQL injection testing

### Security Tools
- **GDB**: Debugging and exploit development
- **WebGoat**: Web application security training
- **Docker**: Containerized environments
- **ChromeDriver**: Automated browser testing

### Cryptographic Libraries
- **PyCryptodome**: Cryptographic primitives
- **SymPy**: Mathematical operations and prime generation

---

## 📊 Performance Metrics

### Side Channel Attack Accuracy
| Model Type | Accuracy | F1-Score | Inference Time |
|------------|----------|----------|----------------|
| Basic | 85.2% | 0.847 | 2.1ms |
| Complex | 92.7% | 0.925 | 3.8ms |
| Attention | 90.1% | 0.898 | 5.2ms |
| Ensemble | 94.1% | 0.939 | 12.3ms |

### Cryptography Performance
- **AES Encryption**: ~50 MB/s (Python implementation)
- **ECDH Key Exchange**: ~500ms for key generation
- **File Transfer**: Encrypted throughput depends on network

---

## 🤝 Contributing

This is primarily an educational repository for CSE-406 coursework. However, improvements and corrections are welcome:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/improvement`)
3. Commit your changes (`git commit -am 'Add improvement'`)
4. Push to the branch (`git push origin feature/improvement`)
5. Open a Pull Request

### Contribution Guidelines
- Maintain educational focus
- Document all changes thoroughly
- Test code before submission
- Follow existing code style
- Add comments for complex logic

---

## 📚 Learning Resources

### Recommended Reading
- **Buffer Overflows**:
  - "Hacking: The Art of Exploitation" by Jon Erickson
  - "The Shellcoder's Handbook" by Chris Anley et al.

- **Cryptography**:
  - "Applied Cryptography" by Bruce Schneier
  - "Cryptography Engineering" by Ferguson, Schneier, and Kohno

- **Web Security**:
  - "The Web Application Hacker's Handbook" by Stuttard and Pinto
  - OWASP Top 10 Web Application Security Risks

- **Side-Channel Attacks**:
  - "The Cache Timing Attack on AES" by Daniel J. Bernstein
  - "Website Fingerprinting through Deep Learning" research papers

### Online Resources
- [OWASP WebGoat](https://owasp.org/www-project-webgoat/)
- [CryptoHack](https://cryptohack.org/)
- [LiveOverflow YouTube Channel](https://www.youtube.com/c/LiveOverflow)
- [Trail of Bits Security Blog](https://blog.trailofbits.com/)

---

## 📄 License

This project is part of academic coursework for CSE-406 Computer Security. The code is provided for educational purposes under standard academic use guidelines.

**Note**: Some components may have their own licenses. Check individual directories for specific license files.

---

## 👥 Authors & Acknowledgments

### Primary Author
- **Md. Amimul Ahsan** - Student ID: 2005017
  - Side Channel Attack implementation and deployment
  - Repository organization and documentation

### Course Information
- **Course**: CSE-406 Computer Security
- **Institution**: Bangladesh University of Engineering and Technology (BUET)
- **Department**: Computer Science and Engineering

### Acknowledgments
- Course instructors for assignment specifications
- OWASP WebGoat project for ethical hacking practice
- Open-source cryptography community
- Security research community

---

## 📞 Contact & Support

### Repository
- **GitHub**: [https://github.com/amimulamim/CSE-406-Computer-Security](https://github.com/amimulamim/CSE-406-Computer-Security)
- **Issues**: Use GitHub Issues for bug reports and questions

### Live Demos
- **Side Channel Attack**: [http://20.40.60.232:5000](http://20.40.60.232:5000) (Educational demo - not for production use)

### Additional Resources
- **Dataset**: [Kaggle - Side Channel Attack Traces](https://www.kaggle.com/datasets/amimulehsan1/side-channel-attack-2005017)
- **Models**: [Kaggle Models](https://www.kaggle.com/models/amimulehsan1/side-channel-attacksweep-count)

---

## 🔖 Keywords

`computer-security` `buffer-overflow` `cryptography` `aes` `ecdh` `sql-injection` `ethical-hacking` `side-channel-attack` `website-fingerprinting` `machine-learning` `python` `c` `security-research` `education` `webgoat` `pytorch` `selenium`

---

**Last Updated**: December 2025

**⚠️ Important**: This repository is for educational purposes only. Always obtain proper authorization before conducting security assessments. Unauthorized access to computer systems is illegal and unethical.
