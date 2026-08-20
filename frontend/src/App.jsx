import "./App.css";

function SensorCard({ icon, title, value, unit, description }) {
  return (
    <div className="sensor-card">
      <div className="sensor-card-header">
        <div className="sensor-icon">{icon}</div>

        <span className="live-tag">
          <span className="status-dot" />
          LIVE
        </span>
      </div>

      <div className="sensor-title">{title}</div>

      <div className="sensor-reading">
        {value !== null ? value : "--"}
        {value !== null && <span>{unit}</span>}
      </div>

      <div className="sensor-description">{description}</div>
    </div>
  );
}

function QualityCard({ contaminationScore }) {
  /*
   * ML MODEL:
   *
   * Higher score = MORE contamination
   *
   * Expected range:
   * 0 → least contamination
   * 10 → highest contamination
   *
   * Therefore:
   *
   * Quality Score = 10 - Contamination Score
   *
   * Then convert:
   *
   * Quality / 10 → Quality / 100
   */

  const qualityScore10 =
    contaminationScore !== null
      ? Math.max(0, Math.min(10, 10 - contaminationScore))
      : null;

  const qualityScore100 =
    qualityScore10 !== null
      ? Math.round(qualityScore10 * 10)
      : null;

  let category = "AWAITING DATA";
  let categoryClass = "waiting";

  if (qualityScore100 !== null) {
    if (qualityScore100 >= 90) {
      category = "EXCELLENT";
      categoryClass = "good";
    } else if (qualityScore100 >= 75) {
      category = "GOOD";
      categoryClass = "good";
    } else if (qualityScore100 >= 50) {
      category = "MODERATE";
      categoryClass = "moderate";
    } else if (qualityScore100 >= 25) {
      category = "POOR";
      categoryClass = "poor";
    } else {
      category = "CRITICAL";
      categoryClass = "critical";
    }
  }

  const progress =
    qualityScore100 !== null
      ? qualityScore100 * 3.6
      : 0;

  return (
    <div className={`quality-card ${categoryClass}`}>

      <div className="quality-top">

        <div>
          <div className="section-label">
            WATER QUALITY
          </div>

          <h2>Overall Assessment</h2>
        </div>

        <div className="quality-category">
          {category}
        </div>

      </div>


      <div className="quality-ring-wrapper">

        <div
          className="quality-ring"
          style={{
            "--progress": `${progress}deg`,
          }}
        >

          <div className="quality-ring-inner">

            <div className="score-number">
              {qualityScore100 !== null
                ? qualityScore100
                : "--"}
            </div>

            <div className="score-total">
              / 100
            </div>

            <div className="quality-label">
              {category}
            </div>

          </div>

        </div>

      </div>


      <div className="quality-details">

        {contaminationScore !== null ? (
          <>
            Contamination score:{" "}
            {contaminationScore.toFixed(1)} / 10
            <br />
            Quality score:{" "}
            {qualityScore10.toFixed(1)} / 10
          </>
        ) : (
          "Waiting for ML contamination score"
        )}

      </div>

    </div>
  );
}


function App() {

  /*
   * HARDWARE + ML DATA
   *
   * These values are intentionally null.
   *
   * Later they will come from the FastAPI backend.
   */

  const sensorData = {

    temperature: null,

    turbidityVoltage: null,

    contaminationScore: null,

    cameraUrl: null,

    deviceOnline: false,

  };


  return (
    <div className="app">

      <div className="background-glow glow-one" />
      <div className="background-glow glow-two" />


      <main className="dashboard">


        {/* HEADER */}

        <header className="header">

          <div className="brand">

            <div className="brand-logo">
              H
            </div>

            <div>

              <h1>HYDROMIND</h1>

              <p>
                Smart Water Quality Intelligence
              </p>

            </div>

          </div>


          <div
            className={`connection-status ${
              sensorData.deviceOnline
                ? "online"
                : "offline"
            }`}
          >

            <span className="connection-dot" />

            {sensorData.deviceOnline
              ? "ESP32 CONNECTED"
              : "ESP32 OFFLINE"}

          </div>

        </header>


        {/* HERO */}

        <section className="hero">

          <div className="hero-label">
            WATER MONITORING SYSTEM
          </div>

          <h2>
            Understand your
            <span> water.</span>
          </h2>

          <p>
            Real-time monitoring of water temperature,
            turbidity output and contamination-based
            water quality using an ESP32-CAM system.
          </p>

        </section>


        {/* CAMERA + QUALITY */}

        <section className="main-grid">


          {/* CAMERA */}

          <div className="camera-card">

            <div className="card-header">

              <div>

                <div className="section-label">
                  VISUAL MONITORING
                </div>

                <h2>
                  Water Sample
                </h2>

              </div>


              <div className="live-label">

                <span />

                CAMERA

              </div>

            </div>


            <div className="camera-container">

              {sensorData.cameraUrl ? (

                <img
                  src={sensorData.cameraUrl}
                  alt="Water sample captured by ESP32-CAM"
                />

              ) : (

                <div className="camera-placeholder">

                  <div className="camera-symbol">

                    <div className="camera-lens" />

                  </div>

                  <h3>
                    Waiting for ESP32-CAM
                  </h3>

                  <p>
                    The water sample image will
                    appear here once the camera
                    connects.
                  </p>

                </div>

              )}


              <div className="camera-overlay">

                <span>
                  ESP32-CAM
                </span>

                <span>
                  LIVE FEED
                </span>

              </div>

            </div>

          </div>


          {/* QUALITY */}

          <QualityCard
            contaminationScore={
              sensorData.contaminationScore
            }
          />

        </section>


        {/* SENSOR CARDS */}

        <section className="sensor-grid">


          <SensorCard
            icon="°"
            title="WATER TEMPERATURE"
            value={sensorData.temperature}
            unit="°C"
            description="DS18B20 waterproof temperature probe"
          />


          <SensorCard
            icon="≈"
            title="TURBIDITY OUTPUT"
            value={sensorData.turbidityVoltage}
            unit=" V"
            description="R-0913 analog voltage output"
          />


          <div className="sensor-card system-card">

            <div className="sensor-card-header">

              <div className="sensor-icon system-icon">
                ◎
              </div>

              <span className="live-tag">
                SYSTEM
              </span>

            </div>


            <div className="sensor-title">
              DEVICE STATUS
            </div>


            <div className="device-state">

              <span
                className={`state-indicator ${
                  sensorData.deviceOnline
                    ? "active"
                    : "inactive"
                }`}
              />

              {sensorData.deviceOnline
                ? "Monitoring Active"
                : "Awaiting Device"}

            </div>


            <div className="sensor-description">
              ESP32-CAM communication status
            </div>

          </div>

        </section>


        {/* WATER SUITABILITY */}

        <section className="suitability-section">

          <div className="section-heading">

            <div>

              <div className="section-label">
                APPLICATION ASSESSMENT
              </div>

              <h2>
                Water Suitability
              </h2>

            </div>

            <span className="assessment-note">
              Based on overall quality score
            </span>

          </div>


          <div className="suitability-grid">


            <div className="suitability-card">

              <div className="suitability-icon">
                💧
              </div>

              <div>

                <span>
                  DRINKING
                </span>

                <h3>
                  Requires Further Testing
                </h3>

                <p>
                  Current sensors cannot certify
                  drinking-water safety.
                </p>

              </div>

            </div>


            <div className="suitability-card">

              <div className="suitability-icon">
                🌱
              </div>

              <div>

                <span>
                  AGRICULTURE
                </span>

                <h3>
                  Assessment Pending
                </h3>

                <p>
                  Classification will use the
                  system quality score.
                </p>

              </div>

            </div>


            <div className="suitability-card">

              <div className="suitability-icon">
                ⚙
              </div>

              <div>

                <span>
                  GENERAL USE
                </span>

                <h3>
                  Assessment Pending
                </h3>

                <p>
                  Suitability will be determined
                  from measured parameters.
                </p>

              </div>

            </div>


          </div>

        </section>


        {/* SENSOR HISTORY */}

        <section className="data-section">

          <div className="section-heading">

            <div>

              <div className="section-label">
                MONITORING
              </div>

              <h2>
                Sensor History
              </h2>

            </div>

            <span className="assessment-note">
              Real-time data visualization
            </span>

          </div>


          <div className="chart-placeholder">

            <div className="chart-icon">
              ↗
            </div>

            <h3>
              Historical data will appear here
            </h3>

            <p>
              Temperature, turbidity voltage and
              quality score will be plotted once
              the ESP32 begins transmitting readings.
            </p>

          </div>

        </section>


        {/* FOOTER */}

        <footer className="footer">

          <span>
            HYDROMIND
          </span>

          <span>
            ESP32-CAM&nbsp;&nbsp;•&nbsp;&nbsp;
            DS18B20&nbsp;&nbsp;•&nbsp;&nbsp;
            R-0913
          </span>

        </footer>


      </main>

    </div>
  );
}

export default App;