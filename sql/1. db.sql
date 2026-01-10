CREATE TABLE IF NOT EXISTS users
(
    id         SERIAL PRIMARY KEY,
    face_name  VARCHAR(255)        NOT NULL,
    email      VARCHAR(100) UNIQUE NOT NULL,
    password   VARCHAR(255)        NOT NULL,
    is_active  BOOLEAN     DEFAULT TRUE,
    role       VARCHAR(50) DEFAULT 'PHARMACIST',
    created_at TIMESTAMP   DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP   DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS medicines
(
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    stock       INT       DEFAULT 0,
    image_path  VARCHAR(255),
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX idx_medicine_name ON medicines (name);

CREATE TABLE IF NOT EXISTS transactions
(
    id               SERIAL PRIMARY KEY,
    user_id          INT REFERENCES users (id) ON DELETE CASCADE,
    mode             VARCHAR(24) NOT NULL, -- Can be IN or OUT
    transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at       TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS transaction_details
(
    id             SERIAL,
    transaction_id INT REFERENCES transactions (id) ON DELETE CASCADE ON UPDATE CASCADE,
    medicine_id    INT REFERENCES medicines (id) ON DELETE CASCADE ON UPDATE CASCADE,
    quantity       INT NOT NULL CHECK (quantity > 0),
    created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS authentication_history
(
    id                 SERIAL,
    user_id            INT REFERENCES users (id) ON DELETE CASCADE ON UPDATE CASCADE,
    time_authenticated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)