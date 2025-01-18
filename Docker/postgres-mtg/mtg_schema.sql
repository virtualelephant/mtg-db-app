DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.tables
        WHERE table_name = 'mtg_cards'
    ) THEN
        CREATE TABLE mtg_cards (
            id SERIAL PRIMARY KEY,
            name TEXT,
            multiverse_id BIGINT,
            layout TEXT,
            names TEXT[], -- Array of alternative card names
            mana_cost TEXT,
            cmc NUMERIC,
            colors TEXT[],
            color_identity TEXT[],
            type TEXT,
            supertypes TEXT[],
            subtypes TEXT[],
            rarity TEXT,
            text TEXT,
            flavor TEXT,
            artist TEXT,
            number TEXT,
            power TEXT,
            toughness TEXT,
            loyalty TEXT,
            variations TEXT[],
            watermark TEXT,
            border TEXT,
            timeshifted BOOLEAN,
            hand INTEGER,
            life INTEGER,
            reserved BOOLEAN,
            release_date DATE,
            starter BOOLEAN,
            rulings JSONB,
            foreign_names JSONB,
            printings TEXT[],
            original_text TEXT,
            original_type TEXT,
            legalities JSONB,
            source TEXT,
            image_url TEXT,
            set TEXT,
            set_name TEXT
        );
    END IF;
END $$;
