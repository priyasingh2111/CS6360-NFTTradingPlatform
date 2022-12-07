#PROCEDURE FOR UPDATING LEVEL ON MONTHLY BASIS
#BASED ON ALL TRANSACTIONS (BUY OR SELL ANY) FOR PAST MONTH 
delimiter //
CREATE PROCEDURE ChangeLevel()
BEGIN
DECLARE last INT DEFAULT 0;
DECLARE start INT DEFAULT 0;
DECLARE total_transaction INT DEFAULT 0;

DECLARE ID VARCHAR(255);
DECLARE circ CURSOR FOR SELECT T.client_id FROM Trader T;     
OPEN circ; 
FETCH NEXT FROM circ INTO ID;

SELECT COUNT(*) FROM Trader INTO last;

SET start=0;
WHILE start <last DO
	SELECT SUM(T.ethereum_value) AS total  FROM Transaction T, Trader T1, TRADER T2 
	WHERE (T.ethereum_buyer_address=T.ethereum_address OR T.ethereum_seller_address=T.ethereum_address) 
    AND T.client_id=ID AND
    DATE(date) BETWEEN DATE_ADD(LAST_DAY(DATE_SUB(NOW(), INTERVAL 2 MONTH)), INTERVAL 1 DAY) 
	AND LAST_DAY(DATE_SUB(NOW(), INTERVAL 1 MONTH)) INTO total_transaction;
    
    IF(total_transaction>100000) THEN
		UPDATE Trader T 
        SET T.level="GOLD" 
        WHERE T.Client_id=ID;
	
    ELSE
		UPDATE Trader T 
        SET T.level="SILVER" 
        WHERE T.Client_id=ID;
	END IF;
	SET start= start+1;
    FETCH NEXT FROM circ INTO ID;
END WHILE;
CLOSE circ ;
End;
//
delimiter ;

DELIMITER $$
IF(DAY(CURRDATE()==1) THEN
	CALL PROCEDURE ChangeLevel();
END IF;
DELIMITER ;

