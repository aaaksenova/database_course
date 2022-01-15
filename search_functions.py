from datetime import timedelta
import datetime
import psycopg2
import seaborn as sns
import pandas as pd


def check_user(cur, phone_number):
    """The function checks if user is authorised"""
    cur.execute("""
    SELECT userid FROM personal_data
    WHERE phonenumber = '%s';
    """ % phone_number)
    data = cur.fetchall()
    if data:
        return True
    else:
        return False


def get_name(cur, phone_number):
    """The function gets user's name if user is younger than 25
    and name + father's name if one is older"""
    cur.execute("""
    SELECT userid,
        CASE WHEN EXTRACT(YEAR FROM AGE(NOW(), dateofbirth)) >= 25 THEN name || ' ' || fathersname
        ELSE name END
    FROM personal_data 
    WHERE phonenumber = '{}';
    """.format(phone_number))
    return cur.fetchall()[0][1]


def get_new_sessionid(cur):
    """The function generates next session id"""
    cur.execute("""SELECT sessionid FROM call_logging ORDER BY sessionid DESC LIMIT 1;""")
    sessionid = cur.fetchall()[0][0] + 1
    return sessionid


def session_logging(cur, conn, phone_number, sessionid, timestampstart, timestampend, productkeyword):
    """
    The function takes all the necessary parameters
    and inserts the data into call_logging table
    """
    cur.execute("""
    SELECT userid,
        CASE WHEN EXTRACT(YEAR FROM AGE(NOW(), dateofbirth)) >= 25 THEN name || ' ' || fathersname
        ELSE name END
    FROM personal_data 
    WHERE phonenumber = '%s';
    """ % phone_number)
    data = cur.fetchall()
    userid = data[0][0]
    callduration = timestampend - timestampstart
    attrs = (sessionid, userid,
             timestampstart.strftime("%m/%d/%Y %H:%M:%S"),
             timestampend.strftime("%m/%d/%Y %H:%M:%S"), callduration.seconds,
             productkeyword)
    cur.execute("""
            INSERT INTO call_logging ( sessionid,
                                       userid,
                                       timestampstart,
                                       timestampend,
                                       callduration,
                                       productkeyword) VALUES {}
            """.format(attrs))
    conn.commit()
    cur.execute("""SELECT subsessionid FROM call_logging ORDER BY subsessionid DESC LIMIT 1;""")
    last_subsession = cur.fetchall()[0][0]
    return last_subsession


def sales_logging(cur, conn, last_subsession, sales_flag):
    """
    The function takes necessary arguments, selects the rest of the information from logs
     and inserts it into sales_logging table
    """
    if sales_flag:
        cur.execute("""
            SELECT call_logging.subsessionid, products.productid

            FROM call_logging

            INNER JOIN products ON call_logging.productkeyword = products.productkeyword

            WHERE call_logging.subsessionid == {};
            """.format(last_subsession))
        saled_log = cur.fetchall()
        cur.execute("""INSERT INTO sales_logging (subsessionid, productid)
        VALUES
            {};
        """.format(saled_log[0]))
        conn.commit()
        cur.execute("""
        SELECT sales_logging.productid, call_logging.timestampend, call_logging.userid

        FROM sales_logging

        INNER JOIN call_logging ON call_logging.subsessionid = sales_logging.subsessionid;
        """)
        personal_product = cur.fetchall()
        personal_product = list(personal_product[0]) + ['call']
        cur.execute("""INSERT INTO user_products (productid, salesdate, userid, saleschannel)
        VALUES
            {};
        """.format((personal_product[0], personal_product[1].strftime("%m/%d/%Y %H:%M:%S"),
                    personal_product[2], personal_product[3])))
        conn.commit()


def csi_logging(cur, conn, csi_flag, last_subsession, solved, csi, comment):
    """
    The function takes necessary arguments and inserts them into session_metrics table
    """
    if csi_flag:
        attrs = (last_subsession, csi, solved, comment)
        cur.execute("""INSERT INTO session_metrics (subsessionid, csi, solvedquestion, comment)
        VALUES
            {};
        """.format(attrs))
        conn.commit()




