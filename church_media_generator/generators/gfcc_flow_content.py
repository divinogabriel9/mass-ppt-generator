"""
GFCC mass flow text (from sample deck Feb 2026). Markers: <<P>> priest, <<A>> all/congregation,
<<D>> direction (italic gold), <<H>> hymn body (white). <<BR>> line break only.

Edit this file to swap hymns, announcements, or wording.
"""

# --- Pre-Mass & entrance ---
SILENT_REMINDER = """<<H>>PUT YOUR CELLPHONE ON SILENT MODE DURING THE MASS.
<<D>>Thank you."""

ENTRANCE_HYMN_1 = """<<H>>SING TO THE MOUNTAINS, SING TO THE SEA
RAISE YOUR VOICES, LIFT YOUR HEARTS
THIS IS THE DAY THE LORD HAS MADE
LET ALL THE EARTH REJOICE
<<D>>Entrance hymn — replace with your chosen song and verses."""

ENTRANCE_HYMN_2 = """<<H>>I WILL GIVE THANKS TO YOU, MY LORD
YOU HAVE ANSWERED MY PLEA
YOU HAVE SAVED MY SOUL FROM DEATH
YOU ARE MY STRENGTH AND MY SONG
<<D>>(Continue verses as needed.)"""

# --- Introductory rites ---
SIGN_CROSS = """<<P>>In the Name of the Father, and of the Son, and of the Holy Spirit.
<<A>>Amen.
<<P>>The Lord be with you.
<<A>>And with your spirit."""

GREETING_EXTENDED = """<<P>>Brothers and sisters, let us acknowledge our sins, and so prepare ourselves to celebrate the sacred mysteries."""

CONFITEOR_OPEN = """<<A>>I confess to almighty God and to you, my brothers and sisters, that I have greatly sinned in my thoughts and in my words, in what I have done and in what I have failed to do; therefore I ask blessed Mary ever-Virgin, all the Angels and Saints, and you, my brothers and sisters, to pray for me to the Lord our God."""

ABSOLUTION_PENITENTIAL = """<<P>>May almighty God have mercy on us, forgive us our sins, and bring us to everlasting life.
<<A>>Amen."""

KYRIE = """<<A>>Lord, have mercy. Christ, have mercy. Lord, have mercy.
<<D>>Kyrie Eleison — sing or recite as customary."""

GLORIA_1 = """<<H>>We praise you, we bless you, we adore you, we glorify you, we give you thanks for your great glory, Lord God, heavenly King, O God, almighty Father."""

GLORIA_2 = """<<H>>Lord Jesus Christ, Only Begotten Son, Lord God, Lamb of God, Son of the Father, you take away the sins of the world, have mercy on us; you take away the sins of the world, receive our prayer; you are seated at the right hand of the Father, have mercy on us."""

GLORIA_3 = """<<H>>For you alone are the Holy One, you alone are the Lord, you alone are the Most High, Jesus Christ, with the Holy Spirit, in the glory of God the Father. Amen."""

OPENING_PRAYER = """<<P>>Let us pray.
<<A>>Amen.
<<D>>— Replace with the Collect of the day from the Missal / lectionary."""

# --- Liturgy of the Word (between section title and readings: handled in code) ---

LITURGY_WORD_TITLE = """<<H>>LITURGY OF THE WORD
<<D>>Section title — commentator may introduce the Liturgy of the Word."""

ALLELUIA_SING = """<<H>>ALLELUIA! ALLELUIA! ALLELUIA! ALLELUIA!
<<D>>Gospel Acclamation — use the verse of the day from the Lectionary."""

ALLELUIA_COMMENTATOR = """<<D>>Commentator reads the verse before the Gospel Acclamation, then the assembly sings the Alleluia."""

GOSPEL_INTRO = """<<P>>The Lord be with you.
<<A>>And with your spirit.
<<P>>A reading from the holy Gospel according to …
<<A>>Glory to you, O Lord!"""

GOSPEL_END = """<<P>>The Gospel of the Lord.
<<A>>Praise to you, Lord Jesus Christ!"""

# --- Creed & Prayer of the Faithful ---
CREED_1 = """<<A>>I believe in one God, the Father almighty, maker of heaven and earth, of all things visible and invisible. I believe in one Lord Jesus Christ, the Only Begotten Son of God, born of the Father before all ages…"""

CREED_2 = """<<A>>For us men and for our salvation he came down from heaven, (all bow) and by the Holy Spirit was incarnate of the Virgin Mary, and became man. For our sake he was crucified under Pontius Pilate, he suffered death and was buried, and rose again on the third day in accordance with the Scriptures."""

CREED_3 = """<<A>>He ascended into heaven and is seated at the right hand of the Father… I believe in the Holy Spirit… I confess one Baptism for the forgiveness of sins and I look forward to the resurrection of the dead and the life of the world to come. Amen."""

PRAYER_FAITHFUL_1 = """<<D>>Prayer of the Faithful — insert petitions for your community.
<<P>>Father, bless your children.
<<A>>Lord, hear our prayer."""

PRAYER_FAITHFUL_2 = """<<P>>Heavenly Father… We ask this through Christ our Lord.
<<A>>Amen."""

# --- Liturgy of the Eucharist ---
OFFERTORY_HYMN = """<<H>>TAKE AND RECEIVE, O LORD, MY LIBERTY…
<<D>>Offertory — replace with your hymn (e.g. Take and Receive)."""

LOE_TITLE = """<<H>>LITURGY OF THE EUCHARIST"""

PRAY_BRETHREN = """<<P>>Pray, brethren, that my sacrifice and yours may be acceptable to God, the almighty Father.
<<A>>May the Lord accept the sacrifice at your hands, for the praise and glory of his name, for our good and the good of all his holy Church."""

PREFACE_DIALOGUE = """<<P>>The Lord be with you.
<<A>>And with your spirit.
<<P>>Lift up your hearts.
<<A>>We lift them up to the Lord.
<<P>>Let us give thanks to the Lord our God.
<<A>>It is right and just."""

PREFACE_ACCLAIM = """<<P>>…we sing the hymn of your praise as without end we acclaim…
<<D>>— Priest continues the Preface from the Missal."""

SANCTUS = """<<H>>Holy, Holy, Holy Lord God of hosts. Heaven and earth are full of your glory. Hosanna in the highest. Blessed is he who comes in the name of the Lord. Hosanna in the highest."""

MYSTERY_FAITH = """<<H>>When we eat this bread and drink this cup, we proclaim your death, O Lord, until you come again.
<<D>>The Mystery of Faith — use the form in the Eucharistic Prayer of the day."""

GREAT_AMEN = """<<A>>Amen.
<<D>>Great Amen — repeat as customary."""

OUR_FATHER_KO_1 = """<<H>>주님의 기도
하늘에 계신 우리 아버지,
아버지 이름 빛나시며
아버지 뜻이 하늘에서와 같이 땅에서도 이루어지소서
저희에게 일용할 양식 주시고,
저희의 죄를 용서하시고
유혹에 빠지지 않게 하시고,
악에서도 저희 구하소서
<<D>>Our Father — Korean (주님의 기도)."""

OUR_FATHER_KO_2 = """<<H>>영광이며 사랑이신 우리 주님께
처음과 같이 이제와 항상 영원히
<<D>>Doxology in Korean as in GFCC practice."""

COMMUNION_RITE_DELIVER = """<<P>>Deliver us, Lord, we pray, from every evil…
<<A>>For the kingdom, the power, and the glory are yours, now and for ever. Amen."""

SIGN_PEACE = """<<P>>The peace of the Lord be with you always.
<<A>>And with your spirit.
<<D>>Let us offer each other the sign of peace."""

LAMB_OF_GOD = """<<H>>Lamb of God, you take away the sins of the world: have mercy on us…
Lamb of God… grant us peace."""

COMMUNION_DIALOGUE = """<<P>>Behold the Lamb of God…
<<A>>Lord, I am not worthy that you should enter under my roof, but only say the word and my soul shall be healed."""

COMMUNION_HYMN = """<<H>>TASTE AND SEE, TASTE AND SEE THE GOODNESS OF THE LORD…
<<D>>Communion hymn — replace with your selection (multiple slides as needed)."""

POST_COMMUNION = """<<P>>Let us pray.
<<A>>Amen.
<<D>>— Post-Communion Prayer of the day."""

# --- Announcements & closing ---
ANNOUNCEMENTS_TITLE = """<<H>>CHURCH ANNOUNCEMENTS
<<D>>Insert your bulletin points on the following slides or edit this deck."""

WELCOME_NEWCOMERS = """<<H>>Welcome newcomers!
<<D>>Photo collage optional."""

CONFESSION_SLIDE = """<<H>>Sacrament of Confession
<<D>>“The Lord never tires of forgiving us; we are the ones who tire of seeking his mercy.” — Pope Francis"""

COLLECTION_PLACEHOLDER = """<<H>>Mass Collection
<<D>>Amount · date · thank you — add 2 Cor 9:7 if desired."""

SPONSORSHIP = """<<H>>Food or Mass Sponsorship
<<D>>Contact your parish coordinator — thank you."""

FB_UPDATES = """<<H>>Updates and Announcements
<<D>>Like and follow: Gwangju Filipino Catholic Community (add QR in slide master later)."""

FINAL_BLESSING = """<<P>>The Lord be with you.
<<A>>And with your spirit.
<<P>>May almighty God bless you, the Father, and the Son, and the Holy Spirit.
<<A>>Amen.
<<P>>Go in peace, glorifying the Lord by your life.
<<A>>Thanks be to God."""

RECESSIONAL_1 = """<<H>>COME! LIVE IN THE LIGHT! SHINE WITH THE JOY AND THE LOVE OF THE LORD!
WE ARE CALLED… TO BE LIGHT FOR THE KINGDOM…
<<D>>Recessional — We Are Called (David Haas). Replace if needed."""

RECESSIONAL_2 = """<<H>>WE ARE CALLED TO ACT WITH JUSTICE. WE ARE CALLED TO LOVE TENDERLY.
WE ARE CALLED TO SERVE ONE ANOTHER, TO WALK HUMBLY WITH GOD."""
