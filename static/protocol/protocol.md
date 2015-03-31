#Implementing the Assembly Coins Protocol
by Andrew Barisser

October 3, 2014

##My Purpose

Assembly Coins is a protocol for managing financial ownership.  It is first and foremost a Colored Coins implementation.  But
it also encompasses advanced Bitcoin tools for managing a business representation alone.  We are building
ways to provably declare contracts on the Blockchain and monitor whether they have been upheld.  Owners will be
able to vote cryptographically on company initiatives.  As many of the functions of ownership as possible will
be extended to the Blockchain itself, above and beyond mere tokenization.

This document seeks to unambiguously explain how to
reverse engineer everything Assembly-Coins related.  I also wish to outline the basis for any design decisions.  My aim
is to empower readers to be able to rebuild Assembly Coins in their own language, if they wish, or to expand upon Assembly Coins
with more sophisticated tools.  Either way, transparency in the operation of the protocol is essential.  Thus far it
has been sorely lacking.

Assembly Coins uses Open Assets to create and write Colored Coins.  This represents a subset of what Assembly Coins
aims to accomplish.  Because every aspect of this technology is nascent and poorly documented, I hope to
improve the clarity of these concepts and their execution.  This will mean that certain concepts are repeated
from other sources; so be it.  I would like to save others the time I spent reverse-engineering Open Assets, and
make Assembly Coins much more intelligible to new users.

Assembly Coins consists of four main areas:
  - Colored Coins
  - Blockchain-Contracts
  - Stakeholder Voting
  - Multisignature Issuance

I will go through each in detail.  Some parts are largely finished.  Others are at the conceptual stage only.

##Colored Coins
###What is a Colored Coin?
A Colored Coin is a token with a particular label that exists, and can move on, the Bitcoin Blockchain.  Trace
amounts of Bitcoin can be watermarked with a certain identity and then further tracked as they are exchanged between addresses.  It
is advantageous to create distinct classes of tokens because they may represent alternative things besides bitcoin-the-currency.  Colored Coins
are also convenient because they inherit the advantages of Bitcoin.  Since they are composed of trace amounts of Bitcoin, they are trivial to move.
They are pseudonymous and provable, just as bitcoins are.  Most importantly, they leverage the double-spending protection of the public consensus ledger, the Bitcoin Blockchain.

Different Colors exist completely independently of one another.  Thus 'RedCoins' are completely separate from 'BlueCoins'.  There
may be any number of different colors, as many possible colors as there are addresses.

####The Issuing Address
Each Color type originates from a single issuing address.  An issuing address is a Bitcoin public address from which all coins of a particular color
are agreed to originate.  This address controls the total supply of that particular color.  They may later issue additional coins within the color they control.
The issuer must be trusted not to inflate the supply of coins maliciously.  However if coins are issued improperly, ie, against the original terms of a particular color, this
can be quickly identified on the Blockchain.

####The Color Address
The color address is a hash string uniquely identifying a color type.  Many different people may attempt to issue 'RedCoins', however 'RedCoins' from
separate issuers will have different color addresses.  Since color addresses are hashes based on Blockchain data, they cannot be designed to match that of another color.
Since color addresses are deterministically linked to data from the Blockchain, specific to the issuer address, it is possible to prove which address is the issuing address, based on its
transactional history.

 - #####Generating the Color Address
 - Take the script in hex of the first input of the first transaction issuing a new coin Color type.
 - Perform a sha256 and then a ripemd-160 hash on the script.  
 - Perform a base58Check encoding on the result.  Use version '0x05'.
 For exact implementation details, see my code: bitsource.py script_to_coloraddress(script)

####Verification
In Bitcoin, metadata may be written at will and be incorporated into the Blockchain.  Thus
metadata must be checked to be internally consistent above and beyond the mere fact
of its inclusion on the Blockchain.  This stands in contrast to Bitcoin itself, where only
consistent data can enter the Blockchain.

Assembly Coins utilizes a database to build the history of Colored Coin metadata.  The protocol
rules govern which metadata is legitimate for inclusion in the database and what is not.  While Assembly
itself manages one such Colored Coin database, it holds no proprietary information.  Anyone can make an
identical database at any time.

####Trust
The Assembly Coins protocol requires no trust, save in the issuing address for each color.  Otherwise,
transactions cannot be forged; all balances are mathematically self-evident on the Blockchain and may be
determined by anyone.  Assembly itself has no power over Colored Coin transactions.

Because coins are issued with declaratory statements also written onto the Blockchain, it is trivial to
determine whether an issuer has upheld his promises, or to read other permanent metadata associated with the color.




###Writing Transactions
This protocol is primarily about reading and writing Bitcoin transactions containing metadata indicating
their meaning beyond Bitcoin.  While Bitcoin has its own internal rules governing the legitimacy of transactions,
this protocol operates one layer of abstraction above, inspecting the blockchain, and using a second tier of rules
to determine what is legitimate.  By following agreed upon rules, we may derive higher level meaning.  Indeed we must if we are to
use Bitcoin beyond its original purpose.

####The Marker Output
All Open Assets transactions have a marker output.  This output is an OP_RETURN output where the metadata is encoded.
Its position among other outputs also carries significance.  Crafting the marker output correctly is probably the trickiest part
of writing Open Assets transactions.

Note that for clarity, the descriptions below are in ASCII, but they must be converted to HEX in the actual Bitcoin transaction itself.
For the original, see https://github.com/OpenAssets/open-assets-protocol/blob/master/specification.mediawiki#Marker_output

Every Marker Output must include the following
  - Protocol Indicator, 2 bytes

      This is always 'OA' in ASCII.
      This indicates that this is an Open Assets transactions and not another kind of message.

  - Version Number, 2 bytes

      This indicates the Open Assets version in use.  Currently set to '0100'

  - Asset Quantity Count, 1-9 Bytes

      This is an integer indicating the number of Colored Asset Outputs in this transaction.  In other words,
      how many separate colored outputs are there?  Do not include regular Bitcoin outputs.  Don't forget to convert to hex.

      In practice, this number should usually be 1 byte.

  - Asset Quantity List, Variable Length

      This is the list of colored asset outputs.  Each item should
      be an integer of the smallest acceptable increment for the Color.
      This list is encoded via LEB-128, which is basically a clever compression schema.
      I had trouble finding a library available on the web in Python.  
      You can see my implementation at /assemblycoins/leb128.py  encode(integer) which converts
      an integer value for each asset quantity to LEB-128 encoded binary.  Convert to Hex and concatenate all
      asset quantities into a string (1 byte per asset).  According to Open Assets, the maximum
      value here is ~2^63, which is approximately 10^19 and thus adequate for all conceivable needs.

  - Metadata Length, 1 byte

      Further metadata may follow what is already in this OP_RETURN.  You must encode the length of the
      additional data here in HEX.  Open Assets claims this could be 1-9 bytes, but since OP_RETURNS have a
      maximum of 40 bytes, there is no need for more than 1 byte here.  Don't forget to format this, and all
      the quantities in the marker outputs, as single bytes, so '1' should be '01' and '100' should be '0100'.

  - Metadata, any length that fits

      You can put any data here whatsoever.  Just remember that all the marker output data
      must fit within the 40 byte maximum.  You should also encode this data as hex.

- Other Issues

  - The Asset Quantity Count must equal the number of listed Asset quantities, or the transaction is invalid
  as a Colored Coin transaction (the Bitcoin component is always valid if it makes it into a block).

  - For transfers, the amount of Colored Inputs for a particular Color must not be less than the amount in outputs.

  - The position of the Marker Output says a lot.  

    - Outputs before the Marker Output are issue new coins from the sending address, no matter what.  If
    the transaction is properly formatted, these are always legitimate without having to consult a database.  

    - Outputs after the Marker Output may be transfers of coins from the sending address.  More on this exact details later.


####Issuance Transactions

  Issuance transactions create new Colored Coins.  Any address may perform an issuance transaction.  However only the
  issuing address for a particular coin color may produce more of coins of that color.  In other words, any address may
  make its own coin, but each color always traces back to its own unique parent address.

  Issuing transactions are the only way new Colored Coins are created.  Since any address may create a colored coin, any
  properly formatted transaction will produce legitimate colored coins.  Thus verification for these transactions is much
  simpler than for transfer transactions; they do not require the maintenance of a database.

  Here is an example of an issuance transaction:
  https://blockchain.info/tx/76f18638370a3d02ad07b8e6d3b27f829b8fcf8e54a483d6525f0be850541809?show_adv=true

  Note the order of the outputs

  - The first output represents the newly created colored coins 'Bitmarks'

  - The second output is the marker output.
    - The hex data of the marker output was the following:
        4f4101000180ade204084269744d61726b73

        Let us inspect this in hex for a moment.  If you are confused consult the parse_colored_tx() function in bitsource.py or consult the original docs

        - '4f41' represents 'OA' in ASCII

        - '0100' represents the version number

        - '0180ade204' is the LEB128 encoded asset quantity list.  Convert to binary and run leb128.py  decode(binary).
        The outcome here should be [10000000]

        - '08' is the hex representation of ASCII length of the metadata

        -  '4f4101000180ade204084269744d61726b73' is the metadata, simply 'BitMarks', the name of the Coin Color.  This is for clarity.

  - If I had wanted BTC change, I could have legitimately added a 3rd output with no change in the marker output's
  metadata, so long as the third output represented BTC only.


####Transfer Transactions

Transfer transactions simply move Colored Coins from one address to another.  Because
any metadata may be written into the Blockchain according to Bitcoin's rules, but not to
those of Assembly Coins, careful parsing and monitoring of the Blockchain are necessary
to interpret Colored Coin data.  

This is an example of a Transfer transaction:
https://blockchain.info/tx/87d3eff0413109bd4074207b7c977ae3db463a9ba5dc55737aad5e3024a8de72

  - Notice that the marker output is the first output.  This means no new coins were issued.

  - The second output is the Colored Coin output.  Notice that is consists of 601 Satoshi.  This is to get
  around dust limits.  This is the output that is marked as Colored and must be used in future transfers from this address.

  - The third output is also Colored, however it is a Colored Change output.  As the sending address had a large
  amount of this particular color, a substantial amount of color change needed to be returned to the sender.

  - The fourth output is Bitcoin change.  It is nice to separate colored outputs into small dust amounts and keep the Bitcoin
  stored in a single large output.  It is crucial never to misspend Colored outputs as normal Bitcoin.

Now let us decode the metadata from the marker output

  - '4f4101000264efcbe10400'

    - '4f41' represents Open Assets

    - '0100' represents the version

    - '02' represents the asset count in hex.  Note that there are 4 total outputs.
    But since only two of them are colored outputs, the asset count is two.

    - '64efcbe10400' decodes to [100, 9987567]

    - This transaction had no other metadata.

- Order based Coloring

    - Order matters in the outputs of asset quantities.  

Note that a single transaction may issue and transfer simultaneously.  However for simplicity,
the Assembly Coins API does not write transactions this way; they are still valid on the Blockchain.

###Reading Transactions
####Modus Operandi
  My Color Database monitors unspent outputs that are known to be legitimate.  It records their color address, what their inputs were,
  their spent status, their Colored Coin and Bitcoin contents, etc.  Reading a block consists of the following flow:

  - Inspect Each transaction for an OP_RETURN code somewhere in its outputs.  Most transactions will not have one.

  - For those that do, parse the metadata in the marker output.  You might think we should check for the transaction's legitimacy at this step, but
  that would be a mistake.  If a transaction is issued, and then its outputs are immediately used as inputs for another transaction, or a whole series of
  transactions, they should be legitimate.  However if multiple interlinked transactions are included in the same block, for example if transaction B depends
  on transaction A, and if you inspect B before you inspect A, you will not be able to authenticate a valid transaction.  
    - My approach here has been, when inspecting Open Assets transactions in a block, to at first assume they are all pseudo-legitimate and to enter them all into the database. If you
    look in the code you will see that they are temporarily labelled as 'illegitimate' in the color_address field.  
    - After every transaction has been inspected, only THEN inspect the legitimacy of each transaction.  This involves the following steps.
      - Sum the asset quantities listed in the metadata.  This is the total colored output for a given color.  
      - Inspect each input and search for it in the database.  Ascertain whether the colored sum of the inputs is greater than
      or equal to the sum of the outputs.  If so, mark the inputs as spent in the database.  Mark the new outputs in the DB as legitimate.
      - If new outputs remain that were not affirmed through this process, delete them from the DB.

    - One thing to consider would be whether it is possible to write circular, mutually dependent colored transactions that affirm each other, but
    do not stem from the correct issuing address.  Thankfully this is not possible, not because of my Colored Coin implementation, but because Bitcoin
    itself does not allow circular output pathways.

###Checking Address Balances
Once a Color Output database has been built, it is simple to check
the balance of a particular address.  Merely select for unspent outputs which
have the desired address as their destination.  For each Color Address type, sum
the color amounts of each output.  

You can use a similar method to monitor the total supply of coins of a particular color.

##Storing Metadata and Provably Upholding Terms
When users create a new coin, merely creating the tokens
is only part of the process.  It is important to issue
a declaration, ennumerating the terms and metadata associated with
the color type.  For instance, if I release 'RedCoins', I should
explain what they represent, how many there will be, or by what proces new
coins may be issued, the name itself, and other metadata.  There needs to
be a way to write this information openly.  Future coinholders should be
able to inspect the Blockchain for the coin distribution, and to read my unadulterated
terms, and see that I have upheld my commitments.

Currently, Colored Coin metadata is held on proprietary servers, off the Blockchain.  This
is a poor solution.  Assembly Coins has started making 'multipart declarations' every time
a new coin color is issued.  These declarations consist of a series of OPRETURNS that may be
concatenated in a certain order to yield a message.  The current version includes the coin name, the
total number issued, and a description, in ASCII.  Because the declaration is on the Blockchain, originating
from the issuing address for each coin Color, it is trivial to link the statement to the issuer.  And it
is impossible to delete, edit, or obfuscate.  New declarations could be issued by the same address, perhaps with amended
terms.  But such changes would have to occur openly.

We are planning improvements to our current system of releasing metadata on the Blockchain.

 - There will be the option of encoding data visibly in ASCII on the Blockchain, but such statements must be
 short and are expensive.
 - There will be another option to include a web link accompanied by a hash.  These may need to be stored
 in separate OPRETURNS for memory reasons, but they may be clearly linked.  The hash will be a hash of the
 terms and metadata document that the coin creator wants to record.  By posting a hash on the Blockchain,
 he proves that the content cannot be altered surreptitiously.  

Proposed new Format of OP_RETURNS for messaging, in ASCII:
 - 'AC', Assembly Coins, 2 bytes
 - '01', Version Number, 2 byte
 - '03', the index position of this OPRETURN in the entire message, 2 bytes  
 - The Message itself, 34 bytes.  This is enough to contain a sha256 hash or a Bitcoin
 public address, or a shortened URL link.  

This adds to 40 bytes, the OPRETURN maximum.  
Messages may be composed of multiple OPRETURNS, in which case they are stitched together
by the index position field.  If the same address issues separate messages are different points in time,
each new message is marked by an OPRETURN with index position='00'.  This means an address may only send one message
per block.

An example Message, in ASCII
'AC011KFHE7w8BhaENAswwryaoccDb6qcT6DbYY' - this encodes a Bitcoin address
'AC01http://coins.assembly.com' - this encodes a URL

The purpose of posting contractual data publicly and ineffaceably on the Blockchain is
for regular users to be able to confirm, totally on their own and trustlessly, that the
original terms of issuance have been upheld.


##Stakeholder Voting
Assembly intends to enable Smart Corporate Governance through
cryptographic voting.  Possession of digital ownership tokens gives
owners the right to vote.  They do so by encrypted their vote with the
private key of the Bitcoin address holding the tokens.  This way,
the outcome of a vote can be determined by inspecting the Blockchain for
the ownership distribution, in addition to unforgeable cryptographic messages
detailing individuals' selections.  Because each encrypted message can be provably
matched with a Bitcoin address that holds some number of tokens, it
is straightforward to verify the weight to accord to each vote.

While these do not constitute Smart Contracts, per se, they are explicity
and unforgeable expressions of the stakeholders' will.

This is a planned feature on Assembly Coins.  We will build an API call
that takes a private key, and a message, and encrypts it server side.  We will
also release code for a client-side signing version.  A separate API call will
allow for encrypted messages to be HTTP POSTed onto a central server for processing and verification.
While Assembly will operate one such server, it has no special place in this schema, and any
independent server would come to the same conclusions.

##Multisig-Managed Organizations

Assembly Coins aims to use Bitcoin's multisignature capabilities to give businesses
advanced tools for managing ownership between disparate actors.  

  - Issuing addresses will be built with multisig.  This means that multiple parties would
  have to sign off on the issuance of additional Colored Coins.  This adds greater security
  to the monetary supply for each coin color.

  - Multisig addresses will exist for businesses to manage their money securely.
  No one individual need be trusted with jointly owned money.  We're working on
  clever ways to distribute this control as much as possible.  One potential route
  would be to generate a new wallet address every so often, created from the public keys
  of the top 20 business stakeholders.  Assets from the old address could be transferred
  to the new one after each creation event.  It would be possible to prove that BTC had
  been transferred to the correct multisig address.

##Multipart Messages
###Writing Messages
###Reading Messages

#####Sources
I have drawn extensively from the Open Assets Protocol Document.  While at times I have repeated things already stated there, I have tried to improve
upon it in terms of clarity and detail.
https://github.com/OpenAssets/open-assets-protocol/blob/master/specification.mediawiki
