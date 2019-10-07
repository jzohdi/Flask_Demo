
def get_keys(os):
    try:
        dotenv = '.env.ini'
        with open(dotenv, 'r') as file:
            content = file.readlines()

        content = [line.strip().split('=') for line in content if '=' in line]
        env_vars = dict(content)
        if file:
            file.close()
        return env_vars

    except:
        return False
