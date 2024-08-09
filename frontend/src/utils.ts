export { get, post, put, del}

interface RequestParams {
    method: string;
    url: string;
    params?: {[key: string]: any};
}

class HttpError extends Error {
    constructor(public statusCode: number, message?: string) {
        super(message);
        this.name = "HttpError";
    }
}

async function request(requestParams: RequestParams): Promise<Response> {
    const options: { [key: string]: any} = {
        method: requestParams.method
    };
    if (requestParams.method === "GET") {
        options.headers = {
            "Accept": "text/html, application/json"
        };
        if (requestParams.params !== undefined) {
            requestParams.url += '?' + (
                new URLSearchParams(requestParams.params)).toString();
        };
    } else {
        options.body = JSON.stringify(requestParams.params);
        options.headers = {
            "Accept": "text/html, application/json",
            "Content-Type": "application/json"
        };
    };
    try {
        const response = await fetch(requestParams.url, options);
        if (!response.ok) {
            throw new HttpError(response.status, `Request failed with status ${response.status}`);
        };
        return response
    } catch (error) {
        if (error instanceof HttpError) {
            console.error(`HTTP Error: ${error.statusCode} - ${error.message}`);
            return Promise.reject(error)

        } else {
            console.error('Unexpected Error:', error);
            return Promise.reject(new Error('An unexpected error occurred.'))
        };
    }
}

const get = (
    url: string, params?: {[key: string]: any}) => request({method: "GET", url, params});
const post = (
    url: string, params?: {[key: string]: any}) => request({method: "POST", url, params});
const put = (
    url: string, params?: {[key: string]: any}) => request({method: "PUT", url, params});
const del = (
    url: string, params?: {[key: string]: any}) => request({method: "DEL", url, params});
