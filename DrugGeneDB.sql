CREATE TABLE "Disease" (
	"diseaseID"	TEXT NOT NULL UNIQUE,
	"diseaseName"	INTEGER NOT NULL UNIQUE,
	PRIMARY KEY("diseaseID")
);

CREATE TABLE "Drug" (
	"drugID"	TEXT NOT NULL UNIQUE,
	"drugName"	TEXT NOT NULL,
	"type"	TEXT,
	"MOA"	TEXT,
	PRIMARY KEY("drugID")
);

CREATE TABLE "Gene" (
	"GeneCardsSymbol"	TEXT NOT NULL UNIQUE,
	"UniProtID"	TEXT UNIQUE,
	"name"	TEXT NOT NULL UNIQUE,
	PRIMARY KEY("GeneCardsSymbol")
);

CREATE TABLE "GeneAssociation" (
	"GeneCardsSymbol"	TEXT NOT NULL,
	"diseaseID"	TEXT NOT NULL,
	CONSTRAINT "Interaction_FK1" FOREIGN KEY("GeneCardsSymbol") REFERENCES "Gene"("GeneCardsSymbol") ON UPDATE CASCADE ON DELETE CASCADE,
	CONSTRAINT "Interaction_FK2" FOREIGN KEY("diseaseID") REFERENCES "Disease"("diseaseID") ON UPDATE CASCADE ON DELETE CASCADE,
	CONSTRAINT "Interaction_PK" PRIMARY KEY("GeneCardsSymbol","diseaseID")
);

CREATE TABLE "IndicatedFor" (
	"diseaseID"	TEXT NOT NULL,
	"drugID"	TEXT NOT NULL,
	"phase"	INTEGER,
	CONSTRAINT "IndicatedFor_FK2" FOREIGN KEY("drugID") REFERENCES "Drug"("drugID") ON UPDATE CASCADE ON DELETE CASCADE,
	CONSTRAINT "IndicatedFor_FK1" FOREIGN KEY("diseaseID") REFERENCES "Disease"("diseaseID") ON UPDATE CASCADE ON DELETE CASCADE,
	CONSTRAINT "IndicatedFor_PK" PRIMARY KEY("diseaseID","drugID")
);

CREATE TABLE "Interaction" (
	"GeneCardsSymbol"	TEXT NOT NULL,
	"drugID"	TEXT NOT NULL,
	"actionType"	TEXT,
	"source"	TEXT,
	CONSTRAINT "Interaction_PK" PRIMARY KEY("GeneCardsSymbol","drugID"),
	CONSTRAINT "Interaction_FK2" FOREIGN KEY("drugID") REFERENCES "Drug"("drugID") ON UPDATE CASCADE ON DELETE CASCADE,
	CONSTRAINT "Interaction_FK1" FOREIGN KEY("GeneCardsSymbol") REFERENCES "Gene"("GeneCardsSymbol") ON UPDATE CASCADE ON DELETE CASCADE
);
