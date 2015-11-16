# MT940-950-GEN
Create an MT940 or MT950 swift cash statement from a csv file.

##CSV
The csv columns represent various swift fields and their components.

| Csv Header                | Swift Field                                            |
|---------------------------|--------------------------------------------------------|
| Sender BIC                | Header   - 1:                                          |
| Receiver BIC              | Header   - 2:                                          |
| Account ID                | 25                                                     |
| Stmt No					| 28C      - **5n**[/5n]                                 |
| Stmt Pg				    | 28C      - 5n**[/5n]**                                 |
| OpBalSign			        | 60a      - **1!a**6!n3!a15d                            |
| OpBalType                 | 60**a**                                                |
| OpBalDate                 | 60a      - 1!a**6!n**3!a15d                            |
| Opening Balance           | 60a      - 1!a6!n3!a**15d**                            |
| Value Date                | 61 *SF1* - **6!n**[4!n]2a[1!a]15d1!a3!c16x[//16x][34x] |
| Entry Date                | 61 *SF2* - 6!n**[4!n]**2a[1!a]15d1!a3!c16x[//16x][34x] |
| D/C                       | 61 *SF3* - 6!n[4!n]**2a**[1!a]15d1!a3!c16x[//16x][34x] |
| Amount                    | 61 *SF5* - 6!n[4!n]2a[1!a]**15d**1!a3!c16x[//16x][34x] |
| Trancode                  | 61 *SF6* - 6!n[4!n]2a[1!a]15d**1!a3!c**16x[//16x][34x] |
| Ref1                      | 61 *SF7* - 6!n[4!n]2a[1!a]15d1!a3!c**16x**[//16x][34x] |
| Ref2                      | 61 *SF8* - 6!n[4!n]2a[1!a]15d1!a3!c16x**[//16x]**[34x] |
| Ref3                      | 61 *SF9* - 6!n[4!n]2a[1!a]15d1!a3!c16x[//16x]**[34x]** |
| ClBalSign                 | 62a      - **1!a**6!n3!a15d                            |
| ClBalType                 | 62**a**                                                |
| ClBalDate                 | 62a      - 1!a**6!n**3!a15d                            |
| Closing Balance           | 62a      - 1!a6!n3!a**15d**                            |
| AvBalSign                 | 64       - **1!a**6!n3!a15d                            |
| AvBalDate                 | 64       - 1!a**6!n**3!a15d                            |
| Closing Available Balance | 64       - 1!a6!n3!a**15d**                            |
| CCY                       | 60a, 62a, & 64 (3!a)                                   |
| Ref4 (MT940 Only)         | 86                                                     |
| TRN						| 20 	   - 16x

##Example

###CSV Input File
``` csv
Sender BIC,Receiver BIC,Account ID,Stmt No,Stmt Pg,OpBalSign,OpBalType,OpBalDate,Opening Balance,Value Date,Entry Date,D/C,Amount,Trancode,Ref1,Ref2,Ref3,ClBalSign,ClBalType,ClBalDate,Closing Balance,AvBalSign,AvBalDate,Closing Available Balance,CCY,Ref4 (MT940 Only),TRN
TEST12A,BANK33GB,000012345,1,1,C,F,14-10-2015,0,15-10-2015,15-10-2015,C,100,S202,Luvly,Spam,,C,M,15-10-2015,99.45,,,,EUR,,
TEST12A,BANK33GB,000012345,1,1,C,F,14-10-2015,0,14-10-2015,15-10-2015,D,0.55,NMSC,What have the,,Romans ever done for us?,C,M,15-10-2015,99.45,,,,EUR,You can put quite a long reference here if you wish. 123456789,
TEST12A,BANK13GB,000012345,1,2,C,M,14-10-2015,99.45,15-10-2015,15-10-2015,RC,"1,618,033,989.00",S101,89Cut down the ,mightiest tree ,WITH A H3RR1NG!!1!1!,D,F,15-10-2015,1618033889,C,15-10-2015,4238.05,EUR,,
TEST12A,PIGGY123,ABC00067,1,1,C,F,05-11-2015,5521.33,02-10-2007,04-11-2015,RD,"3,200.00",DRFT,AHH SHH,TEST IT,TA TEST IT REAL GOOD,C,F,05-11-2015,3112.54,,,,USD,,
TEST12A,PIGGY123,ABC00067,1,1,C,F,05-11-2015,5521.33,03-11-2015,04-11-2015,C,2.32,STRF,,,,C,F,05-11-2015,3112.54,,,,USD,,
TEST12A,PIGGY123,ABC00067,1,1,C,F,05-11-2015,5521.33,05-11-2015,05-11-2015,D,"5,611.11",NCHG,,66332707721194,          TEN SPACES,C,F,05-11-2015,3112.54,,,,USD,0012993826188276493882993884322,
TEST12A,PIGGY123,ABC00070,1,1,C,F,09-11-2015,9288176.01,09-11-2015,10-11-2015,D,-9000000.01,S123,,,0000 That’s a lot of money,D,M,09-11-2015,"11,824.00",,,,GBP,PPPPPPPPPP    989289899++== S101!!!,KNIGHTSOFNEE1234
TEST12A,PIGGY123,ABC00070,1,1,C,F,09-11-2015,9288176.01,09-11-2015,10-11-2015,D,-300000,S000,SPAM SPAM SPAM,,,D,M,09-11-2015,"11,824.00",,,,GBP,"98008777 REF1678803999 ADRS 789 Python Avenue, Spamtown Ph:555-123-9876",
TEST12A,PIGGY123,ABC00070,1,2,D,M,10-11-2015,"11,824.00",10-11-2015,10-11-2015,C,1,S00S,000122222,93884893,123123125444,D,F,10-11-2015,11789.67,,,,GBP,,
TEST12A,PIGGY123,ABC00070,1,2,D,M,10-11-2015,"11,824.00",10-11-2015,10-11-2015,C,33.33,S  T,X,CHEESY DIBBLES,,D,F,10-11-2015,11789.67,D,10-11-2015,1789.67,GBP,The last item to go. Goodbye everyone.,
```

###MT950
Field 86 (Ref4) is ignored.
```
{1:A21TEST12AXXXXX0000000000}{2:I950BANK33GBXXXXN}{3:{118:MT940950GEN}{4:
:20:MT94050GEN000000
:25:000012345
:28C:00001/00001
:60F:C151014EUR0
:61:1510151015C100S202Luvly//Spam
:61:1510141015D0,55NMSCWhat have the//
Romans ever done for us?
:62M:C151015EUR99,45
-}{5:}
{1:A21TEST12AXXXXX0000000000}{2:I950BANK13GBXXXXN}{3:{118:MT940950GEN}{4:
:20:MT94050GEN000001
:25:12345
:28C:00001/00002
:60M:C151014EUR99,45
:61:1510151015RC1618033989,00S10189Cut down the //mightiest tree 
WITH A H3RR1NG!!1!1!
:62F:D151015EUR1618033889
:64:C151015EUR4238,05
-}{5:}
{1:A21TEST12AXXXXX0000000000}{2:I950PIGGY123XXXXN}{3:{118:MT940950GEN}{4:
:20:MT94050GEN000002
:25:ABC00067
:28C:00001/00001
:60F:C151105USD5521,33
:61:0710021104RD3200,00DRFTAHH SHH//TEST IT
TA TEST IT REAL GOOD
:61:1511031104C2,32STRF//
:61:1511051105D5611,11NCHG//66332707721194
          TEN SPACES
:62F:C151105USD3112,54
:20:KNIGHTSOFNEE1234
:25:ABC00070
:28C:00001/00001
:60F:C151109GBP9288176,01
:61:1511091110D9000000,01S123//
0000 That’s a lot of money
:61:1511091110D300000S000SPAM SPAM SPAM//
:62M:D151109GBP11824,00
:20:MT94050GEN000003
:25:ABC00070
:28C:00001/00002
:60M:D151110GBP11824,00
:61:1511101110C1S00S000122222//93884893
123123125444
:61:1511101110C33,33S  TX//CHEESY DIBBLES
:62F:D151110GBP11789,67
:64:D151110GBP1789,67
-}{5:}
```

###MT940
```
{1:A21TEST12AXXXXX0000000000}{2:I940BANK33GBXXXXN}{3:{118:MT940950GEN}{4:
:20:MT94050GEN000000
:25:000012345
:28C:00001/00001
:60F:C151014EUR0
:61:1510151015C100S202Luvly//Spam
:61:1510141015D0,55NMSCWhat have the//
Romans ever done for us?
:86:You can put quite a long reference here if you wish. 123456789
:62M:C151015EUR99,45
-}{5:}
{1:A21TEST12AXXXXX0000000000}{2:I940BANK13GBXXXXN}{3:{118:MT940950GEN}{4:
:20:MT94050GEN000001
:25:12345
:28C:00001/00002
:60M:C151014EUR99,45
:61:1510151015RC1618033989,00S10189Cut down the //mightiest tree 
WITH A H3RR1NG!!1!1!
:62F:D151015EUR1618033889
:64:C151015EUR4238,05
-}{5:}
{1:A21TEST12AXXXXX0000000000}{2:I940PIGGY123XXXXN}{3:{118:MT940950GEN}{4:
:20:MT94050GEN000002
:25:ABC00067
:28C:00001/00001
:60F:C151105USD5521,33
:61:0710021104RD3200,00DRFTAHH SHH//TEST IT
TA TEST IT REAL GOOD
:61:1511031104C2,32STRF//
:61:1511051105D5611,11NCHG//66332707721194
          TEN SPACES
:86:0012993826188276493882993884322
:62F:C151105USD3112,54
:20:KNIGHTSOFNEE1234
:25:ABC00070
:28C:00001/00001
:60F:C151109GBP9288176,01
:61:1511091110D9000000,01S123//
0000 That’s a lot of money
:86:PPPPPPPPPP    989289899++== S101!!!
:61:1511091110D300000S000SPAM SPAM SPAM//
:86:98008777 REF1678803999 ADRS 789 Python Avenue, Spamtown Ph:555-123-9876
:62M:D151109GBP11824,00
:20:MT94050GEN000003
:25:ABC00070
:28C:00001/00002
:60M:D151110GBP11824,00
:61:1511101110C1S00S000122222//93884893
123123125444
:61:1511101110C33,33S  TX//CHEESY DIBBLES
:86:The last item to go. Goodbye everyone.
:62F:D151110GBP11789,67
:64:D151110GBP1789,67
-}{5:}
```

##WARNING!
The program only validates that the file is of csv type, and that the right header is present. **No** validation is performed against the actual data to ensure that it complies with the field restrictions or swift standards.
