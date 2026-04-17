let currentQRPayload = null;

// Generate Secure QR
async function generateSecureQR() {
  const data = document.getElementById("inputData").value;
  if (!data) {
    showLog("❌ Please enter data first", "error");
    return;
  }

  showLog("🔄 Encrypting data and generating QR Code...", "info");
  document.getElementById("generateBtn").disabled = true;

  try {
    const response = await fetch("/api/secure_qr", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ data: data }),
    });

    const result = await response.json();

    if (result.success) {
      // Display QR Code
      document.getElementById("qrPreview").style.display = "block";
      document.getElementById("qrImage").src =
        "data:image/png;base64," + result.qr_image;

      // Save payload for verification
      const payload = JSON.stringify({
        encrypted: result.encrypted_data,
        hash: result.hash,
      });
      currentQRPayload = payload;
      document.getElementById("qrPayload").value = payload;

      showLog(
        `
                        ✅ Secure QR Code created successfully!
                        🔐 Encrypted data: ${result.encrypted_data.substring(0, 50)}...
                        🔑 Hash: ${result.hash.substring(0, 32)}...
                        📝 Original data: "${result.original_data}"
                    `,
        "success",
      );
    } else {
      showLog(
        "❌ Failed to create QR Code: " + (result.error || "Unknown error"),
        "error",
      );
    }
  } catch (error) {
    showLog("❌ Server connection error: " + error.message, "error");
  } finally {
    document.getElementById("generateBtn").disabled = false;
  }
}

// Verify QR
async function verifyQR() {
  const payload = document.getElementById("qrPayload").value;
  if (!payload) {
    showLog("❌ Please enter QR payload to verify", "error");
    return;
  }

  showLog("🔄 Decrypting and verifying integrity...", "info");

  try {
    const response = await fetch("/api/verify_qr", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ payload: payload }),
    });

    const result = await response.json();

    if (result.success && result.verified) {
      showLog(
        `
                        ✅ <strong>Verification Successful!</strong><br>
                        📄 Decrypted data: "${result.decrypted_data}"<br>
                        🔒 Data is intact and has not been tampered with
                    `,
        "success",
      );
    } else if (result.success && !result.verified) {
      showLog(
        `
                        ⚠️ <strong>Tampering Detected!</strong><br>
                        🔓 Decrypted data: "${result.decrypted_data}"<br>
                        ❌ Hash mismatch - Data has been modified
                    `,
        "error",
      );
    } else {
      showLog(
        "❌ Verification failed: " + (result.error || "Invalid data"),
        "error",
      );
    }
  } catch (error) {
    showLog("❌ Error: " + error.message, "error");
  }
}

// Simulate Tampering
async function simulateTamper() {
  const payload = document.getElementById("qrPayload").value;
  if (!payload) {
    showLog("❌ Please create a QR Code first", "error");
    return;
  }

  showLog("🔧 Simulating tampering attack...", "info");

  try {
    const response = await fetch("/api/tamper_test", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ payload: payload }),
    });

    const result = await response.json();

    if (result.success) {
      document.getElementById("qrPayload").value = result.tampered_payload;
      showLog(
        "⚠️ Data has been maliciously modified! Now click 'Verify & Check' to detect tampering.",
        "error",
      );
    }
  } catch (error) {
    showLog("❌ Failed to simulate tampering", "error");
  }
}

function showLog(message, type) {
  const logBox = document.getElementById("logBox");
  logBox.innerHTML = message;
  logBox.className = "log-box";
  if (type === "error") logBox.classList.add("error");
  else if (type === "success") logBox.classList.add("success");
}

// Load default demo data
window.onload = () => {
  document.getElementById("inputData").value =
    "https://secure-payment-system.com/user=admin&token=secure123";
};
