/**
 * Simple msgpack decoder cho các message cơ bản
 * Hỗ trợ: fixmap, fixstr, fixint, nil, bool, float64
 */

function decodeMessage(buffer) {
	let offset = 0;
	const uint8Array = new Uint8Array(buffer);

	function read() {
		if (offset >= uint8Array.length) return null;

		const byte = uint8Array[offset++];

		// Positive fixint (0x00 - 0x7f)
		if (byte <= 0x7f) return byte;

		// Fixmap (0x80 - 0x8f)
		if (byte >= 0x80 && byte <= 0x8f) {
			const size = byte & 0x0f;
			const obj = {};
			for (let i = 0; i < size; i++) {
				const key = read();
				const value = read();
				obj[key] = value;
			}
			return obj;
		}

		// Fixarray (0x90 - 0x9f)
		if (byte >= 0x90 && byte <= 0x9f) {
			const size = byte & 0x0f;
			const arr = [];
			for (let i = 0; i < size; i++) {
				arr.push(read());
			}
			return arr;
		}

		// Fixstr (0xa0 - 0xbf)
		if (byte >= 0xa0 && byte <= 0xbf) {
			const len = byte & 0x1f;
			const strBytes = uint8Array.slice(offset, offset + len);
			offset += len;
			return new TextDecoder().decode(strBytes);
		}

		// nil (0xc0)
		if (byte === 0xc0) return null;

		// false (0xc2)
		if (byte === 0xc2) return false;

		// true (0xc3)
		if (byte === 0xc3) return true;

		// float 64 (0xcb)
		if (byte === 0xcb) {
			const view = new DataView(uint8Array.buffer, offset, 8);
			offset += 8;
			return view.getFloat64(0);
		}

		// uint 8 (0xcc)
		if (byte === 0xcc) {
			return uint8Array[offset++];
		}

		// uint 16 (0xcd)
		if (byte === 0xcd) {
			const view = new DataView(uint8Array.buffer, offset, 2);
			offset += 2;
			return view.getUint16(0);
		}

		// uint 32 (0xce)
		if (byte === 0xce) {
			const view = new DataView(uint8Array.buffer, offset, 4);
			offset += 4;
			return view.getUint32(0);
		}

		// int 8 (0xd0)
		if (byte === 0xd0) {
			const val = uint8Array[offset++];
			return val > 127 ? val - 256 : val;
		}

		// int 16 (0xd1)
		if (byte === 0xd1) {
			const view = new DataView(uint8Array.buffer, offset, 2);
			offset += 2;
			return view.getInt16(0);
		}

		// int 32 (0xd2)
		if (byte === 0xd2) {
			const view = new DataView(uint8Array.buffer, offset, 4);
			offset += 4;
			return view.getInt32(0);
		}

		// str 8 (0xd9)
		if (byte === 0xd9) {
			const len = uint8Array[offset++];
			const strBytes = uint8Array.slice(offset, offset + len);
			offset += len;
			return new TextDecoder().decode(strBytes);
		}

		// str 16 (0xda)
		if (byte === 0xda) {
			const view = new DataView(uint8Array.buffer, offset, 2);
			const len = view.getUint16(0);
			offset += 2;
			const strBytes = uint8Array.slice(offset, offset + len);
			offset += len;
			return new TextDecoder().decode(strBytes);
		}

		// array 16 (0xdc)
		if (byte === 0xdc) {
			const view = new DataView(uint8Array.buffer, offset, 2);
			const size = view.getUint16(0);
			offset += 2;
			const arr = [];
			for (let i = 0; i < size; i++) {
				arr.push(read());
			}
			return arr;
		}

		// map 16 (0xde)
		if (byte === 0xde) {
			const view = new DataView(uint8Array.buffer, offset, 2);
			const size = view.getUint16(0);
			offset += 2;
			const obj = {};
			for (let i = 0; i < size; i++) {
				const key = read();
				const value = read();
				obj[key] = value;
			}
			return obj;
		}

		// Negative fixint (0xe0 - 0xff)
		if (byte >= 0xe0) {
			return byte - 256;
		}

		log("⚠️ Unknown msgpack byte: 0x" + byte.toString(16));
		return null;
	}

	return read();
}

/**
 * Encode message thành binary đơn giản
 * Dùng cho các message cơ bản như pong
 */
function encodeMessage(obj) {
	const parts = [];

	function encode(value) {
		if (value === null) {
			parts.push(0xc0);
		} else if (typeof value === "boolean") {
			parts.push(value ? 0xc3 : 0xc2);
		} else if (typeof value === "number") {
			if (Number.isInteger(value)) {
				if (value >= 0 && value <= 127) {
					parts.push(value);
				} else if (value >= -32 && value < 0) {
					parts.push(value + 256);
				} else if (value >= 0 && value <= 255) {
					parts.push(0xcc, value);
				} else if (value >= 0 && value <= 65535) {
					parts.push(0xcd, (value >> 8) & 0xff, value & 0xff);
				}
			} else {
				// Float - skip for simplicity, không cần cho pong
			}
		} else if (typeof value === "string") {
			const bytes = new TextEncoder().encode(value);
			if (bytes.length <= 31) {
				parts.push(0xa0 | bytes.length);
			} else if (bytes.length <= 255) {
				parts.push(0xd9, bytes.length);
			}
			for (const b of bytes) parts.push(b);
		} else if (Array.isArray(value)) {
			if (value.length <= 15) {
				parts.push(0x90 | value.length);
			}
			for (const item of value) encode(item);
		} else if (typeof value === "object") {
			const keys = Object.keys(value);
			if (keys.length <= 15) {
				parts.push(0x80 | keys.length);
			}
			for (const key of keys) {
				encode(key);
				encode(value[key]);
			}
		}
	}

	encode(obj);
	return new Uint8Array(parts);
}

// Export functions so this file can be imported as an ES module
export { encodeMessage, decodeMessage };
