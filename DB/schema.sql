-- noinspection SqlNoDataSourceInspectionForFile

CREATE EXTENSION IF NOT EXISTS hstore;

-- User related tables

CREATE TABLE IF NOT EXISTS nyapixuser ( -- user table
    id SERIAL PRIMARY KEY,
    username TEXT NOT NULL,
    nickname TEXT NOT NULL,
    password TEXT NOT NULL, -- hashed using bcrypt
    user_type INT NOT NULL CHECK (user_type IN (1, 2, 3)), -- 1: admin, 2: user, 3: guest
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (username)
);

CREATE TABLE IF NOT EXISTS nyapixuser_session ( -- user session table
    id SERIAL PRIMARY KEY,
    user_id INT NOT NULL,
    session_id TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES nyapixuser(id) ON DELETE CASCADE
);

-- DATA related tables

CREATE TABLE IF NOT EXISTS nyapixdata ( -- data table
    id SERIAL PRIMARY KEY,
    bytes BYTEA NOT NULL,
    file_hash TEXT NOT NULL, -- hashed using SHA256
    file_format TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS nyapixdata_miniature ( -- miniature data table
    id SERIAL PRIMARY KEY,
    data_id INT NOT NULL,
    bytes BYTEA NOT NULL,
    hash TEXT NOT NULL,
    FOREIGN KEY (data_id) REFERENCES nyapixdata(id) ON DELETE CASCADE
);

-- content & albums related tables

CREATE TABLE IF NOT EXISTS nyapixcontent (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    user_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_id INT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES nyapixuser(id) ON DELETE CASCADE,
    FOREIGN KEY (data_id) REFERENCES nyapixdata(id)
);

CREATE TABLE IF NOT EXISTS nyapixalbum (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    user_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    miniature_id INT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES nyapixuser(id) ON DELETE CASCADE,
    FOREIGN KEY (miniature_id) REFERENCES nyapixdata_miniature(id)
);

CREATE TABLE IF NOT EXISTS nyapixguest_content_authorizations ( -- guest authorizations table
    id SERIAL PRIMARY KEY,
    guest_id INT NOT NULL,
    content_id INT NOT NULL,
    FOREIGN KEY (guest_id) REFERENCES nyapixuser(id) ON DELETE CASCADE,
    FOREIGN KEY (content_id) REFERENCES nyapixcontent(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS nyapixguest_album_authorizations ( -- guest authorizations table
    id SERIAL PRIMARY KEY,
    guest_id INT NOT NULL,
    album_id INT NOT NULL,
    FOREIGN KEY (guest_id) REFERENCES nyapixuser(id) ON DELETE CASCADE,
    FOREIGN KEY (album_id) REFERENCES nyapixalbum(id) ON DELETE CASCADE
);

-- Tags & authors related tables

CREATE TABLE IF NOT EXISTS nyapixtag ( -- tag table
    id SERIAL PRIMARY KEY,
    tag_name TEXT NOT NULL,
    user_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (tag_name),
    FOREIGN KEY (user_id) REFERENCES nyapixuser(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS nyapixauthor ( -- author table
    id SERIAL PRIMARY KEY,
    author_name TEXT NOT NULL,
    user_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (author_name),
    FOREIGN KEY (user_id) REFERENCES nyapixuser(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS nyapixcharacters ( -- character table
    id SERIAL PRIMARY KEY,
    character_name TEXT NOT NULL,
    user_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (character_name),
    FOREIGN KEY (user_id) REFERENCES nyapixuser(id) ON DELETE CASCADE
    );

CREATE TABLE IF NOT EXISTS nyapixcontent_tag ( -- content tag table
    content_id INT NOT NULL,
    tag_id INT NOT NULL,
    PRIMARY KEY (content_id, tag_id),
    FOREIGN KEY (content_id) REFERENCES nyapixcontent(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES nyapixtag(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS nyapixcontent_author ( -- content author table
    content_id INT NOT NULL,
    author_id INT NOT NULL,
    PRIMARY KEY (content_id, author_id),
    FOREIGN KEY (content_id) REFERENCES nyapixcontent(id) ON DELETE CASCADE,
    FOREIGN KEY (author_id) REFERENCES nyapixauthor(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS nyapixcontent_characters ( -- content characters table
    content_id INT NOT NULL,
    character_id INT NOT NULL,
    PRIMARY KEY (content_id, character_id),
    FOREIGN KEY (content_id) REFERENCES nyapixcontent(id) ON DELETE CASCADE,
    FOREIGN KEY (character_id) REFERENCES nyapixcharacters(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS nyapixalbum_tag ( -- album tag table
    album_id INT NOT NULL,
    tag_id INT NOT NULL,
    PRIMARY KEY (album_id, tag_id),
    FOREIGN KEY (album_id) REFERENCES nyapixalbum(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES nyapixtag(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS nyapixalbum_author ( -- album author table
    album_id INT NOT NULL,
    author_id INT NOT NULL,
    PRIMARY KEY (album_id, author_id),
    FOREIGN KEY (album_id) REFERENCES nyapixalbum(id) ON DELETE CASCADE,
    FOREIGN KEY (author_id) REFERENCES nyapixauthor(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS nyapixalbum_pages ( -- album pages table
    album_id SERIAL PRIMARY KEY,
    data_id INT NOT NULL,
    page_number INT NOT NULL,
    FOREIGN KEY (album_id) REFERENCES nyapixalbum(id) ON DELETE CASCADE,
    FOREIGN KEY (data_id) REFERENCES nyapixdata(id) ON DELETE CASCADE
);

-- User history related tables

CREATE TABLE IF NOT EXISTS nyapixuser_content_history ( -- user content history table
    user_id INT NOT NULL,
    content_id INT NOT NULL,
    accessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    access_type INT NOT NULL CHECK (access_type IN (1, 2, 3)), -- 1:view, 2:download, 3:edit
    PRIMARY KEY (user_id, content_id),
    FOREIGN KEY (user_id) REFERENCES nyapixuser(id) ON DELETE CASCADE,
    FOREIGN KEY (content_id) REFERENCES nyapixcontent(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS nyapixuser_album_history ( -- user album history table
    user_id INT NOT NULL,
    album_id INT NOT NULL,
    accessed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    access_type INT NOT NULL CHECK (access_type IN (1, 2, 3)), -- 1:view, 2:download, 3:edit
    PRIMARY KEY (user_id, album_id),
    FOREIGN KEY (user_id) REFERENCES nyapixuser(id) ON DELETE CASCADE,
    FOREIGN KEY (album_id) REFERENCES nyapixalbum(id) ON DELETE CASCADE
);

-- Check if there are any references of a data in the nyapixcontent and nyapixalbum tables
CREATE OR REPLACE FUNCTION check_references()
RETURNS TRIGGER AS $$
BEGIN
    IF EXISTS (SELECT 1 FROM nyapixcontent WHERE data_id = OLD.id) OR EXISTS (SELECT 1 FROM nyapixalbum WHERE miniature_id = OLD.id) THEN
        RAISE EXCEPTION 'Cannot delete nyapixdata with id % because it is still referenced in nyapixcontent or nyapixalbum', OLD.id;
END IF;
RETURN OLD;
END;
$$ LANGUAGE plpgsql;

-- Trigger nyapixdata references check before deletion
CREATE TRIGGER before_delete_nyapixdata
BEFORE DELETE ON nyapixdata
FOR EACH ROW
EXECUTE FUNCTION check_references();

-- Check if there are any references of a miniature data in the nyapixalbum table
CREATE OR REPLACE FUNCTION check_references_miniature()
RETURNS TRIGGER AS $$
BEGIN
    IF EXISTS (SELECT 1 FROM nyapixalbum WHERE miniature_id = OLD.id) THEN
        RAISE EXCEPTION 'Cannot delete nyapixdata_miniature with id % because it is still referenced in nyapixalbum', OLD.id;
END IF;
RETURN OLD;
END;
$$ LANGUAGE plpgsql;

-- Trigger nyapixdata_miniature references check before deletion
CREATE TRIGGER before_delete_nyapixdata_miniature
BEFORE DELETE ON nyapixdata_miniature
FOR EACH ROW
EXECUTE FUNCTION check_references_miniature();
